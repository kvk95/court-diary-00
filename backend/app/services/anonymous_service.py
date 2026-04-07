from datetime import datetime
from typing import Optional

from passlib.utils import generate_password
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData
from app.database.models.users import Users
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.anonymous_dtos import ServerDateTimeOut
from app.dtos.users_dto import UserCreateBasic, UserPasswordIn
from app.utils.security import hash_password
from app.validators import aggregate_errors
from app.validators.error_codes import ErrorCodes
from app.validators.field_validations import FieldValidator
from app.validators.validation_errors import ValidationErrorDetail

from .base.base_service import BaseService


class AnonymousService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        users_repo: Optional[UsersRepository] = None,
        user_chamber_link_repo: Optional[UserChamberLinkRepository] = None,
            
    ):
        super().__init__(session)
        self.users_repo = users_repo or UsersRepository()
        self.user_chamber_link_repo = user_chamber_link_repo or UserChamberLinkRepository()

    async def _check_user_chamber_membership(self, email: str) -> dict:
        """
        Check user's chamber membership status.
        """
        # Get user INCLUDING deleted (use raw query, not get_first)
        stmt = select(Users).where(Users.email == email.lower())
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return {"exists": False}
        
        return {
            "exists": True,
            "user": user,
            "user_id": user.user_id,
            "deleted_ind": user.deleted_ind,
            "status_ind": user.status_ind,
        }    
 
    async def _validate_user_payload(
        self,
        payload:UserCreateBasic,
        *,
        is_edit: bool = False,
    ) -> None:
        """
        Shared field-level validation for UserCreate and UserEdit.
 
        For add  (is_edit=False): email, first_name, and password are required.
        For edit (is_edit=True) : all three are optional; only validated when present.
        Raises via aggregate_errors so the caller gets one consolidated error response.
        """
        errors = []
 
        # ── email ──────────────────────────────────────────────────────────
        if not is_edit:
            if err := FieldValidator.validate_email(payload.email):
                errors.append(err)
 
        # ── first_name ─────────────────────────────────────────────────────
        if not is_edit and not payload.first_name:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="first_name is required",
                )
            )
 
        if errors:
            aggregate_errors(errors=errors)

    async def _reactivate_user(self, user_id: str) -> None:
        """Undelete a user - delegates to repository."""
        await self.users_repo.reactivate_deleted_user(
            session=self.session,
            user_id=user_id,
        )

    async def get_server_datetime(self) -> ServerDateTimeOut:
        """
        Returns the current date/time formatted as ISO string.
        """
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        return ServerDateTimeOut(server_datetime=formatted)

    async def get_all_refm(self) -> RefmData:
        return await RefmCache.get(session=self.session)
 
    async def users_add(self, payload: UserCreateBasic) -> str:
        email:str = payload.email if payload.email else ''
        first_name:str = payload.first_name if payload.first_name else ''
        password:str = generate_password()
        payload.password = password
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        await self._validate_user_payload(payload, is_edit=False)
 
        # ─────────────────────────────────────────────
        # 2. CHECK MEMBERSHIP
        # ─────────────────────────────────────────────
        # Note: active_links is intentionally not fetched here — we only need
        # exists / deleted_ind to decide create-vs-reactivate.
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            if membership["deleted_ind"] or not membership["status_ind"]:
                raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Email already registered, but not active, try Reset Profile to activate User "
                    )
            else:
                raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Email already registered, if you forgoot your password try forgot password"
                    )


 
        # ─────────────────────────────────────────────
        # 3. CREATE USER
        # ─────────────────────────────────────────────
        user = await self.users_repo.create(
            session=self.session,
            data={
                "email": email.lower(),
                "first_name": first_name.strip(),
                "last_name": (payload.last_name or "").strip() or None,
                "password_hash": hash_password(password),
                "status_ind": False,
            },
        )

        #TODO: send email link
        return "User created Successfully, check email for Activation"
 
    async def users_reset(self, email:str) -> str:
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        if err := FieldValidator.validate_email(email):
            raise err
 
        # ─────────────────────────────────────────────
        # 2. CHECK MEMBERSHIP
        # ─────────────────────────────────────────────
        # Note: active_links is intentionally not fetched here — we only need
        # exists / deleted_ind to decide create-vs-reactivate.
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            user = membership["user"]
            await self._reactivate_user(user.user_id)
        else:
            raise ValidationErrorDetail(
                    code=ErrorCodes.NOT_FOUND,
                    message="Email not Found",
                )

        #TODO: send email link
        return "Check email for Activation"
 
    async def users_password_reset(self, email:str) -> str:
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        if err := FieldValidator.validate_email(email):
            raise err
 
        # ─────────────────────────────────────────────
        # 2. CHECK MEMBERSHIP
        # ─────────────────────────────────────────────
        # Note: active_links is intentionally not fetched here — we only need
        # exists / deleted_ind to decide create-vs-reactivate.
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            if membership["deleted_ind"] or not membership["status_ind"]:
                raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Email not active, try Reset Profile to activate User "
                    )
            else:
                raise ValidationErrorDetail(
                        code=ErrorCodes.NOT_FOUND,
                        message="Email not Found",
                    )

        #TODO: send email link
        return "Check email to reset password"
    
    
 
    async def users_new_password(self, email:str, payload: UserPasswordIn) -> str:
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        if err := FieldValidator.validate_email(email):
            raise err
 
        # ─────────────────────────────────────────────
        # 2. CHECK MEMBERSHIP
        # ─────────────────────────────────────────────
        # Note: active_links is intentionally not fetched here — we only need
        # exists / deleted_ind to decide create-vs-reactivate.
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            if membership["deleted_ind"]:
                raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Email not active, try Reset Profile to activate User "
                    )
        else:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Email not Found",
            )
        
        if err := FieldValidator.validate_password(payload.password):
                raise err
        
        user: Users = membership["user"]
        
        update_data: dict = {
                "status_ind": True,
            }
 
        if payload.password:
            update_data["password_hash"] = hash_password(payload.password)
 
        if update_data:
            await self.users_repo.update(
                session=self.session,
                id_values=user.user_id,
                data=update_data,
            )

        #TODO: send email link
        return "Password Changed Sussessfully, relogin"

