from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.validators import ErrorCodes, ValidationErrorDetail
from app.database.models.user_chamber_link import UserChamberLink
from sqlalchemy import select
from app.database.repositories.login_audit_repository import LoginAuditRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.user_profiles_repository import UserProfilesRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.oauth_dtos import LoginRequest, RefreshRequest, TokenOut
from app.utils.security import verify_password
from app.database.models.refm_login_status import RefmLoginStatusConstants
from .base.base_service import BaseService


class AuthService(BaseService):
    """
    Authentication service that orchestrates login, refresh, and user context retrieval.
    """

    def __init__(
        self,
        session: AsyncSession,
        users_repo: UsersRepository | None = None,
        audit_repo: LoginAuditRepository | None = None,
        user_profiles_repo: UserProfilesRepository | None = None,
        role_permissions_repo: RolePermissionsRepository | None = None,
    ):
        super().__init__(session)
        self.users_repo = users_repo or UsersRepository()
        self.audit_repo = audit_repo or LoginAuditRepository()
        self.user_profiles_repo = user_profiles_repo or UserProfilesRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()

    async def login(self, loginRequest: LoginRequest) -> TokenOut:
        """
        Authenticate user and return access/refresh tokens with user context.
        - Validates credentials
        - Logs audit entries for success/failure
        - Issues tokens with authoritative claims from DB
        """
        print(f"LoginRequest: {loginRequest}")

        # ✅ 1. Find user by email (chamber-agnostic at this point)
        user = await self.users_repo.get_first(
            self.session,
            filters={self.users_repo.model.email: loginRequest.email},
            where=[self.users_repo.model.status_ind == True],
        )

        if not user:
            await self.audit_repo.log_login(
                self.session,
                user_id=None,
                loginRequest=loginRequest,
                status_code=RefmLoginStatusConstants.FAILED,
                failure_reason="User not found",
            )
            raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="User not found")

        # ✅ 2. Verify password
        if not verify_password(loginRequest.password, user.password_hash):
            await self.audit_repo.log_login(
                self.session,
                user_id=user.user_id,
                loginRequest=loginRequest,
                status_code=RefmLoginStatusConstants.FAILED,
                failure_reason="Invalid password",
            )
            raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="Invalid credentials")

        # ✅ 3. Resolve user's PRIMARY chamber (or use loginRequest.chamber_id if provided)
        chamber_id = loginRequest.chamber_id  # ✅ Optional: User can specify chamber at login
        if not chamber_id:
            
            
            stmt = select(UserChamberLink.chamber_id).where(
                UserChamberLink.user_id == user.user_id,
                UserChamberLink.is_primary == True,
                UserChamberLink.left_date == None,
                UserChamberLink.status_ind == True,
            )
            result = await self.session.execute(stmt)
            row = result.first()
            if not row:
                raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="User has no active chamber membership")
            chamber_id = row.chamber_id

        # ✅ 4. Success audit (include chamber_id)
        await self.audit_repo.log_login(
            self.session,
            user_id=user.user_id,
            loginRequest=loginRequest,
            status_code=RefmLoginStatusConstants.SUCCESS,
            failure_reason=None,
            chamber_id=chamber_id,  # ✅ Log which chamber was accessed
        )

        # ✅ 5. Authoritative claims from DB (include chamber_id)
        extra_claims = {
            "chamber_id": chamber_id,  # ✅ Changed from company_id
            "user_id": user.user_id,
        }

        access_token = create_access_token(subject=str(user.user_id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.user_id), extra_claims=extra_claims)

        # ✅ 6. Build user context (for THIS chamber)
        user_details = await self.get_user_context(
            self.session, 
            user_id=user.user_id, 
            chamber_id=chamber_id  # ✅ Pass chamber for contextual permissions
        )

        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_details=user_details,
        )

    async def refresh(
        self, session: AsyncSession, refreshRequest: RefreshRequest
    ) -> TokenOut:
        """
        Refresh tokens using a valid refresh token.
        """
        payload = decode_token(refreshRequest.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        subject = payload.get("sub")
        chamber_id = payload.get("chamber_id")  # ✅ Preserve chamber from original token
        
        if not subject:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch current user state (active check)
        user = await self.users_repo.get_first(
            session,
            filters={self.users_repo.model.user_id: int(subject)},
            where=[self.users_repo.model.status_ind == True],
        )
        if not user:
            raise HTTPException(status_code=401, detail="Session expired")

        extra_claims = {
            "chamber_id": chamber_id,  # ✅ Keep same chamber
            "user_id": user.user_id,
        }
        
        access_token = create_access_token(subject=str(subject), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(subject), extra_claims=extra_claims)

        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def get_user_context(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        chamber_id: Optional[int] = None,  # ✅ NEW: For contextual permissions
    ) -> Optional[Dict[str, Any]]:
        """
        Assemble complete user context for a specific chamber.
        """
        # 1. Resolve user + profile + role via repository (with chamber context)
        row = await self.users_repo.get_user_with_profile_and_role(
            session, email=email, user_id=user_id, chamber_id=chamber_id
        )
        if not row:
            return None

        user, profile, role_obj = row

        # 2. Role dictionary
        role: Optional[Dict[str, Any]] = None
        if role_obj:
            role = {
                "role_id": role_obj.role_id,
                "role_name": role_obj.role_name,
            }

        # 3. Permissions via RolePermissionsRepository (chamber-specific)
        permissions: list[dict] = []
        if role_obj and chamber_id:
            permissions = await self.role_permissions_repo.get_permissions_for_login(
                session, 
                role_id=role_obj.role_id, 
                chamber_id=chamber_id
            )

        # 4. Final shape
        return {
            "user": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": role,
                "image": "/assets/images/avatar/none.png",  # ✅ Default (no image column)
            },
            "profile": {
                "theme": {
                    "header_color": (profile.header_color if profile else None) or "0 0% 100%",
                    "sidebar_color": (profile.sidebar_color if profile else None) or "0 0% 100%",
                    "primary_color": (profile.primary_color if profile else None) or "32.4 99% 63%",
                    "font_family": (profile.font_family if profile else None) or "Nunito, sans-serif",
                }
            },
            "permissions": permissions,
            "chamber_id": chamber_id,  # ✅ Include in context
        }