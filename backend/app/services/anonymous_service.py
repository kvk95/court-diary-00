from datetime import datetime
from typing import Optional

from passlib.utils import generate_password
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData
from app.database.models.email_link import EmailLink
from app.database.models.refm_email_templates import RefmEmailTemplatesEnum
from app.database.models.refm_plan_types import RefmPlanTypesConstants
from app.database.models.users import Users
from app.database.repositories.chamber_repository import ChamberRepository
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.anonymous_dtos import ServerDateTimeOut
from app.dtos.users_dto import UserCreateBasic, UserEmailIn, UserPasswordIn
from app.services.EmailLinkService import EmailLinkService
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
        chamber_repo: Optional[ChamberRepository] = None,
        users_repo: Optional[UsersRepository] = None,
        user_chamber_link_repo: Optional[UserChamberLinkRepository] = None,            
    ):
        super().__init__(session)
        self.chamber_repo:ChamberRepository = chamber_repo or ChamberRepository()
        self.users_repo:UsersRepository = users_repo or UsersRepository()
        self.user_chamber_link_repo:UserChamberLinkRepository = user_chamber_link_repo or UserChamberLinkRepository()
        
        self.email_link_service = EmailLinkService( session=self.session )

    async def _check_user_chamber_membership(self, email: str) -> dict:
        """
        Check user's chamber membership status.
        """
        # Get user INCLUDING deleted (use raw query, not get_first)
        user = await self.users_repo.get_first(session=self.session,
                                                 where = [Users.email == email.lower()])
        
        if not user:
            return {"exists": False}
        
        # Check all chamber links
        all_links = await self.user_chamber_link_repo.get_all_active_links_for_user(
            session=self.session,
            user_id=user.user_id,
        )
        
        return {
            "exists": True,
            "user": user,
            "user_id": user.user_id,
            "deleted_ind": user.deleted_ind,
            "status_ind": user.status_ind,
            "active_links": all_links,
            "active_chambers_count": len(all_links),
            "active_chamber_ids": [link.chamber_id for link in all_links],
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
            status_ind=True,
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
        laset_name: str|None = (payload.last_name or "").strip() or None
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
                "last_name": laset_name,
                "password_hash": hash_password(password),
                "status_ind": False,
            },
        )        
 
        # ─────────────────────────────────────────────
        # 4. Create chamber for User
        # ─────────────────────────────────────────────
        updated_chamber = await self.chamber_repo.create(
            session=self.session,
            data = {
                "chamber_name":self.get_initials(first_name,laset_name ),
                "email": email.lower(),
                "plan_code": RefmPlanTypesConstants.FREE
            }
        )
        chamber_id = updated_chamber.chamber_id
 
        # ─────────────────────────────────────────────
        # 5. CREATE CHAMBER LINK
        # ─────────────────────────────────────────────
        await self.user_chamber_link_repo.create(
            session=self.session,
            data={
                "user_id": user.user_id,
                "chamber_id": chamber_id,
                "left_date": None,
                "status_ind": True,
                "primary_ind": True,
            },
        )

        link_url = await self.email_link_service.generate_link(
            user_id=user.user_id,
            email=user.email,
            template_code=RefmEmailTemplatesEnum.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION
        )

        return f"User created Successfully, check email for Activation link {link_url}"
 
    async def resendactivationlink(self, payload:UserEmailIn) -> str:

        email:Optional[str] = payload.email
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        if err := FieldValidator.validate_email(email):
            raise err
        
        email = email or "" # just to avoid compilation error
 
        # ─────────────────────────────────────────────
        # 2. CHECK MEMBERSHIP
        # ─────────────────────────────────────────────
        # Note: active_links is intentionally not fetched here — we only need
        # exists / deleted_ind to decide create-vs-reactivate.
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            user:Users = membership["user"]
            if membership["deleted_ind"] or not membership["status_ind"]:
                link_url = await self.email_link_service.generate_link(
                    user_id=user.user_id,
                    email=user.email,
                    template_code=RefmEmailTemplatesEnum.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION
                )
            else:
                raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Email already activte, if you forgoot your password try forgot password"
                    )
           
        return f"Check email for Activation link {link_url}"
 
    async def users_reset(self, link_id: str) -> str:

        email_link_row:EmailLink = await self.email_link_service.verify_link(encrypted_id=link_id)

        if not email_link_row:
            raise ValidationErrorDetail(
                    code=ErrorCodes.NOT_FOUND,
                    message="Invalid link",
                )        

        user_row:Users = await self.users_repo.get_first(session=self.session,
                                                 where = [Users.user_id == email_link_row.user_id])
        if not user_row:
            raise ValidationErrorDetail(
                    code=ErrorCodes.NOT_FOUND,
                    message="Invalid link",
                )     

        email:str = user_row.email
 
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
        
        return "User Activated successfully relogin"
 
    async def users_password_reset(self, payload:UserEmailIn) -> str:
        # ─────────────────────────────────────────────
        # 1. VALIDATION
        # ─────────────────────────────────────────────
        email:str = payload.email or ""
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

        user = membership["user"]
        link_url = await self.email_link_service.generate_link(
            user_id=user.user_id,
            email=user.email,
            template_code=RefmEmailTemplatesEnum.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION
        )
        return f"Check email to reset password : {link_url}"
 
    async def users_new_password(self, link_id: str,payload: UserPasswordIn) -> str:

        email_link_row:EmailLink = await self.email_link_service.verify_link(encrypted_id=link_id)

        if not email_link_row:
            raise ValidationErrorDetail(
                    code=ErrorCodes.NOT_FOUND,
                    message="Invalid link",
                )        

        user_row:Users = await self.users_repo.get_first(session=self.session,
                                                 where = [Users.user_id == email_link_row.user_id])
        if not user_row:
            raise ValidationErrorDetail(
                    code=ErrorCodes.NOT_FOUND,
                    message="Invalid link",
                )     

        email:str = user_row.email
 
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

