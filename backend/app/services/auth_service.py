# app/services/auth_service.py

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.database.models.chamber import Chamber
from app.database.repositories.chamber_repository import ChamberRepository
from app.dtos.chamber_dto import ChamberOut
from app.validators import ErrorCodes, ValidationErrorDetail
from app.database.models.user_chamber_link import UserChamberLink
from sqlalchemy import desc, select
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
        chamber_repo: Optional[ChamberRepository] = None,
        users_service: UsersService | None = None,  # ← Inject UsersService
    ):
        super().__init__(session)        
        self.chamber_repo = chamber_repo or ChamberRepository()
        self.users_repo = users_repo or UsersRepository()
        self.audit_repo = audit_repo or LoginAuditRepository()
        self.user_profiles_repo = user_profiles_repo or UserProfilesRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()
        self.users_service = users_service  # ← Use for get_user_full_details

    
    
    def _to_out(self, chamber: Chamber) -> ChamberOut:
        return ChamberOut(
            chamber_id=chamber.chamber_id,
            chamber_name=chamber.chamber_name,
            email=chamber.email,
            phone=chamber.phone,
            address_line1=chamber.address_line1,
            address_line2=chamber.address_line2,
            city=chamber.city,
            state_code=chamber.state_code,
            postal_code=chamber.postal_code,
            country_code=chamber.country_code,
            plan_code=chamber.plan_code,
            subscription_start=chamber.subscription_start,
            subscription_end=chamber.subscription_end,
            status_ind=chamber.status_ind,
            created_date=chamber.created_date,
            updated_date=chamber.updated_date,
        )
    
    async def _get_chamber(self, chamber_id:str) -> Chamber:
        """Fetch chamber scoped to the authenticated chamber_id."""
        chamber = await self.chamber_repo.get_by_id(
            session=self.session,
            filters={Chamber.chamber_id: chamber_id},
        )
        if not chamber:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Chamber not found",
            )
        return chamber

    async def _get_chambers(self, chamber_ids: list[str]) -> list[Chamber]:
        stmt = select(Chamber).where(Chamber.chamber_id.in_(chamber_ids))
        result = await self.session.execute(stmt)
        chambers = result.scalars().all()

        if not chambers:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="No chambers found",
            )

        return list(chambers)

    async def login(self, loginRequest: LoginRequest, is_regular: bool = True) -> TokenOut:
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

        if chamber_id:
            chamber_rows = [await self._get_chamber(chamber_id=chamber_id)]
        else:
            stmt = select(UserChamberLink.chamber_id).where(
                UserChamberLink.user_id == user.user_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind == True,
            ).order_by(desc(UserChamberLink.primary_ind))

            result = await self.session.execute(stmt)
            
            chamber_ids = [row.chamber_id for row in result]

            if not chamber_ids:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="User has no active chamber membership"
                )

            # ✅ fetch ALL chambers using IN clause
            chamber_rows = await self._get_chambers(chamber_ids)

            # optional: keep primary first
            chamber_id = chamber_ids[0]

        # 4. Success audit
        await self.audit_repo.log_login(
            self.session,
            user_id=user.user_id,
            loginRequest=loginRequest,
            status_code=RefmLoginStatusConstants.SUCCESS,
            failure_reason=None,
            chamber_id=chamber_id,
        )

        is_temp = (
            is_regular
            and not loginRequest.chamber_id
            and len(chamber_rows) != 1
        )

        temp_claim = "Y" if is_temp else ""

        # 5. Create tokens
        extra_claims = {
            "chamber_id": chamber_id,
            "user_id": user.user_id,
            "temp_claim": temp_claim,
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
        chamber_details = []

        if is_regular:        
            chamber_details =  [ self._to_out(chamber=row)
                for row in chamber_rows
            ]

        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_details=user_details,
            chamber_details=chamber_details,
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
            filters={self.users_repo.model.user_id: str(subject)},
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
            chamber_details=[],
        )