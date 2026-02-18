from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.validators import ErrorCodes, ValidationErrorDetail
from app.database.repositories.login_audit_repository import LoginAuditRepository
from app.database.repositories.role_permissions_repository import (
    RolePermissionsRepository,
)
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
        self.role_permissions_repo = (
            role_permissions_repo or RolePermissionsRepository()
        )

    async def login(self, loginRequest: LoginRequest) -> TokenOut:
        """
        Authenticate user and return access/refresh tokens with user context.
        - Validates credentials
        - Logs audit entries for success/failure
        - Issues tokens with authoritative claims from DB
        """
        # Find active user by email
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
            raise ValidationErrorDetail(code= ErrorCodes.VALIDATION_ERROR,message= "User not found")

        # Verify password
        if not verify_password(loginRequest.password, user.password_hash):
            await self.audit_repo.log_login(
                self.session,
                user_id=user.user_id,
                loginRequest=loginRequest,
                status_code=RefmLoginStatusConstants.FAILED,
                failure_reason="Invalid password",
            )
            raise ValidationErrorDetail(code= ErrorCodes.VALIDATION_ERROR,message= "Invalid credentials")

        # Success audit
        await self.audit_repo.log_login(
            self.session,
            user_id=user.user_id,
            loginRequest=loginRequest,
            status_code=RefmLoginStatusConstants.SUCCESS,
            failure_reason=None,
        )

        # Authoritative claims from DB
        extra_claims = {"company_id": user.company_id}

        access_token = create_access_token(
            subject=user.user_id, extra_claims=extra_claims
        )
        refresh_token = create_refresh_token(
            subject=user.user_id, extra_claims=extra_claims
        )

        # Build user context (user/profile/localization/permissions)
        user_details = await self.get_user_context(self.session, user_id=user.user_id)

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
        - Validates token and subject
        - Verifies current user is still active
        - Issues new tokens with authoritative claims from DB
        """
        payload = decode_token(refreshRequest.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch current user state (active check)
        user = await self.users_repo.get_first(
            session,
            filters={self.users_repo.model.user_id: subject},
            where=[self.users_repo.model.status_ind == True],
        )
        if not user:
            raise HTTPException(status_code=401, detail="Session expired")

        extra_claims = {"company_id": user.company_id}
        access_token = create_access_token(subject=subject, extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=subject, extra_claims=extra_claims)

        return TokenOut(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def get_user_context(
        self,
        session: AsyncSession,
        *,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Assemble complete user context:
        - user core fields
        - profile theme (with safe defaults)
        - localization settings (with defaults if missing)
        - permissions for role (login variant)
        Exactly one of `email` or `user_id` must be provided.
        """

        # 1. Resolve user + profile + role via repository
        row = await self.users_repo.get_user_with_profile_and_role(
            session, email=email, user_id=user_id
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

        # # 3. Localization settings (with defaults if none)
        # loc_row = await self.localization_repo.get_first(
        #     session, filters={self.localization_repo.model.company_id: user.company_id}
        # )
        # if not loc_row:
        #     localization = self.localization_repo.default_dict()
        #     localization["company_id"] = user.company_id
        # else:
        #     localization = {
        #         "company_id": loc_row.company_id,
        #         "language": loc_row.language,
        #         "show_language_switcher": loc_row.show_language_switcher,
        #         "timezone": loc_row.timezone,
        #         "date_format": loc_row.date_format,
        #         "time_format": loc_row.time_format,
        #         "financial_year": loc_row.financial_year,
        #         "starting_month": loc_row.starting_month,
        #         "currency": loc_row.currency,
        #         "currency_symbol": "?",
        #         "currency_position": loc_row.currency_position,
        #         "decimal_separator": loc_row.decimal_separator,
        #         "thousand_separator": loc_row.thousand_separator,
        #         "country_restriction": loc_row.country_restriction,
        #         "allowed_file_types": loc_row.allowed_file_types,
        #         "max_file_size_mb": loc_row.max_file_size_mb,
        #     }

        #     localization["currency_symbol"] = await self.refm_resolver.from_column(
        #         column_attr=self.localization_repo.model.currency,
        #         code=loc_row.currency,
        #         value_column="symbol",
        #         default="?",
        #     )

        # 4. Permissions via RolePermissionsRepository
        permissions: list[dict] = []
        if role_obj:
            permissions = await self.role_permissions_repo.get_permissions_for_login(
                session, role_id=role_obj.role_id, company_id=user.company_id
            )

        # 5. Final shape
        return {
            "user": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": role,
                "image": user.image,
            },
            "profile": {
                "theme": {
                    "header_color": (profile.header_color if profile else None)
                    or "0 0% 100%",
                    "sidebar_color": (profile.sidebar_color if profile else None)
                    or "0 0% 100%",
                    "primary_color": (profile.primary_color if profile else None)
                    or "32.4 99% 63%",
                    "font_family": (profile.font_family if profile else None)
                    or "Nunito, sans-serif",
                }
            },
            # "localization": localization,
            "permissions": permissions,
        }
