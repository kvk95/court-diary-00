# app/services/auth_service.py

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
from app.services.users_service import UsersService  # ← Import UsersService
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
        users_service: UsersService | None = None,  # ← Inject UsersService
    ):
        super().__init__(session)
        self.users_repo = users_repo or UsersRepository()
        self.audit_repo = audit_repo or LoginAuditRepository()
        self.user_profiles_repo = user_profiles_repo or UserProfilesRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()
        self.users_service = users_service  # ← Use for get_user_full_details

    async def login(self, loginRequest: LoginRequest) -> TokenOut:
        """
        Authenticate user and return access/refresh tokens with user context.
        """
        print(f"LoginRequest: {loginRequest}")

        # 1. Find user by email
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

        # 2. Verify password
        if not verify_password(loginRequest.password, user.password_hash):
            await self.audit_repo.log_login(
                self.session,
                user_id=user.user_id,
                loginRequest=loginRequest,
                status_code=RefmLoginStatusConstants.FAILED,
                failure_reason="Invalid password",
            )
            raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="Invalid credentials")

        # 3. Resolve user's PRIMARY chamber
        chamber_id = loginRequest.chamber_id
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

        # 4. Success audit
        await self.audit_repo.log_login(
            self.session,
            user_id=user.user_id,
            loginRequest=loginRequest,
            status_code=RefmLoginStatusConstants.SUCCESS,
            failure_reason=None,
            chamber_id=chamber_id,
        )

        # 5. Create tokens
        extra_claims = {
            "chamber_id": chamber_id,
            "user_id": user.user_id,
        }

        access_token = create_access_token(subject=str(user.user_id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.user_id), extra_claims=extra_claims)

        # 6. Get user details via UsersService (single source of truth)
        # Create temporary UsersService with the resolved chamber_id
        users_service = UsersService(
            session=self.session
        )
        user_details = await users_service.get_user_full_details(user_id=user.user_id,
                                                                 chamber_id=chamber_id)

        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_details=user_details,
        )

    async def refresh(
        self, session: AsyncSession, refreshRequest: RefreshRequest
    ) -> TokenOut:
        """Refresh tokens using a valid refresh token."""
        payload = decode_token(refreshRequest.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        subject = payload.get("sub")
        chamber_id = payload.get("chamber_id")
        
        if not subject:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await self.users_repo.get_first(
            session,
            filters={self.users_repo.model.user_id: int(subject)},
            where=[self.users_repo.model.status_ind == True],
        )
        if not user:
            raise HTTPException(status_code=401, detail="Session expired")

        extra_claims = {
            "chamber_id": chamber_id,
            "user_id": user.user_id,
        }
        
        access_token = create_access_token(subject=str(subject), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(subject), extra_claims=extra_claims)

        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )