from datetime import datetime
from typing import Any, Optional

from passlib.utils import generate_password
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData
from app.database.models.chamber_modules import ChamberModules
from app.database.models.email_link import EmailLink
from app.database.models.refm_email_templates import RefmEmailTemplatesEnum
from app.database.models.refm_modules import RefmModulesConstants
from app.database.models.refm_plan_types import RefmPlanTypesConstants
from app.database.models.users import Users
from app.database.repositories.chamber_modules_repository import ChamberModulesRepository
from app.database.repositories.chamber_repository import ChamberRepository
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.database.repositories.role_permission_master_repository import RolePermissionMasterRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.user_roles_repository import UserRolesRepository
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
        chamber_module_repo: Optional[ChamberModulesRepository] = None,
        security_role_repo: Optional[SecurityRolesRepository] = None,
        chamber_role_repo: Optional[ChamberRolesRepository] = None,
        user_role_repo: Optional[UserRolesRepository] = None,
        role_permission_master_repo: Optional[RolePermissionMasterRepository] = None,
        role_permission_repo: Optional[RolePermissionsRepository] = None,
        email_link_service: Optional[EmailLinkService] = None,
    ):
        super().__init__(session)
        self.chamber_repo: ChamberRepository = chamber_repo or ChamberRepository()
        self.users_repo: UsersRepository = users_repo or UsersRepository()
        self.user_chamber_link_repo: UserChamberLinkRepository = user_chamber_link_repo or UserChamberLinkRepository()
        self.chamber_module_repo: ChamberModulesRepository = chamber_module_repo or ChamberModulesRepository()
        self.security_role_repo: SecurityRolesRepository = security_role_repo or SecurityRolesRepository()
        self.chamber_role_repo: ChamberRolesRepository = chamber_role_repo or ChamberRolesRepository()
        self.user_role_repo: UserRolesRepository = user_role_repo or UserRolesRepository()
        self.role_permission_master_repo: RolePermissionMasterRepository = role_permission_master_repo or RolePermissionMasterRepository()
        self.role_permission_repo: RolePermissionsRepository = role_permission_repo or RolePermissionsRepository()
        self.email_link_service = email_link_service or EmailLinkService(session=self.session)

    # ─────────────────────────────────────────────────────────────────────────
    # PERMISSION MATRIX  ·  data-driven, no hard-coded role names in loops
    # ─────────────────────────────────────────────────────────────────────────

    _ROLE_PERMISSION_MATRIX: dict[str, dict[str, dict[str, bool]]] = {
        "Administrator": {
            # sentinel → full access on every module
            "__all__": dict(
                allow_all_ind=True,
                read_ind=True,
                write_ind=True,
                create_ind=True,
                delete_ind=True,
                import_ind=True,
                export_ind=True,
            )
        },
        "Senior Advocate": {
            RefmModulesConstants.ADMIN: dict(
                allow_all_ind=False, read_ind=False, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.DASHBOARD: dict(
                allow_all_ind=False, read_ind=True, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.CASES: dict(
                allow_all_ind=False, read_ind=True, write_ind=True,
                create_ind=True, delete_ind=False, import_ind=True, export_ind=True,
            ),
            RefmModulesConstants.HEARINGS: dict(
                allow_all_ind=False, read_ind=True, write_ind=True,
                create_ind=True, delete_ind=False, import_ind=True, export_ind=True,
            ),
            RefmModulesConstants.CALENDAR: dict(
                allow_all_ind=False, read_ind=True, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.CLIENTS: dict(
                allow_all_ind=False, read_ind=True, write_ind=True,
                create_ind=True, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.BILLING: dict(
                allow_all_ind=False, read_ind=True, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.USER_MANAGEMENT: dict(
                allow_all_ind=False, read_ind=False, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.REPORTS: dict(
                allow_all_ind=False, read_ind=True, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=True,
            ),
            RefmModulesConstants.SETTINGS: dict(
                allow_all_ind=False, read_ind=True, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
            RefmModulesConstants.COLLABORATIONS: dict(
                allow_all_ind=False, read_ind=False, write_ind=False,
                create_ind=False, delete_ind=False, import_ind=False, export_ind=False,
            ),
        },
    }

    _DEFAULT_PERMISSION: dict[str, bool] = dict(
        allow_all_ind=False,
        read_ind=True,
        write_ind=False,
        create_ind=False,
        delete_ind=False,
        import_ind=False,
        export_ind=False,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SETUP CHAMBER SECURITY  (steps 3 → 6)
    # ─────────────────────────────────────────────────────────────────────────

    async def _setup_chamber_security(
        self,
        *,
        chamber_id: str,
        user_id: str,
        user_chamber_link_id: str,
    ) -> None:
        """
        3. Add all refm_modules → chamber_modules
        4. Copy security_roles  → chamber_roles
        5. Link user            → Administrator chamber_role
        6. Set role_permissions for every role × module (bulk insert)
        """

        # ── 3. MODULES ────────────────────────────────────────────────────────
        # Fix #1: correct resolver call — column_attr=ChamberModules.module_code
        modules: dict[str, Any] = await self.refm_resolver.get_refm_map(
            column_attr=ChamberModules.module_code
        )

        created_modules: list[Any] = await self.chamber_module_repo.bulk_create(
            session=self.session,
            data_list=[
                {
                    "chamber_id": chamber_id,
                    "module_code": module_code,
                    "active_ind": True,
                    "created_by": user_id,
                }
                for module_code in modules
            ],
        )

        # Fix #2: correct Any import and type hint
        chamber_modules_map: dict[str, Any] = {
            cm.module_code: cm for cm in created_modules
        }

        # ── 4. ROLES ──────────────────────────────────────────────────────────
        security_roles = await self.security_role_repo.list_all(session=self.session)

        created_roles: list[Any] = await self.chamber_role_repo.bulk_create(
            session=self.session,
            data_list=[
                {
                    "chamber_id": chamber_id,
                    "role_name": role.role_name,
                    "description": role.description,
                    "admin_ind": role.admin_ind,
                    "system_ind": role.system_ind,
                    "created_by": user_id,
                }
                for role in security_roles
            ],
        )

        # Fix #2: correct Any import and type hint
        chamber_roles_map: dict[str, Any] = {
            cr.role_name: cr for cr in created_roles
        }

        # ── 5. ASSIGN ADMINISTRATOR ROLE TO USER ──────────────────────────────
        # Fix #4: safer lookup + improved error message
        admin_role = chamber_roles_map.get("Administrator")
        if not admin_role:
            raise ValueError(
                "Administrator role not found in security_roles. Ensure seed data exists."
            )

        await self.user_role_repo.create(
            session=self.session,
            data={
                "link_id": user_chamber_link_id,
                "role_id": admin_role.role_id,
                "created_by": user_id,
            },
        )

        # ── 6. ROLE PERMISSIONS  (bulk, DB-driven) ─────────────────────────────

        # 1. Load templates
        templates = await self.role_permission_master_repo.list_all(
            session=self.session
        )

        # 2. Build map: role_name → module_code → permissions
        template_map: dict[str, dict[str, dict[str, Any]]] = {}

        for t in templates:
            template_map.setdefault(t.role_name, {})[t.module_code] = {
                "allow_all_ind": t.allow_all_ind,
                "read_ind": t.read_ind,
                "write_ind": t.write_ind,
                "create_ind": t.create_ind,
                "delete_ind": t.delete_ind,
                "import_ind": t.import_ind,
                "export_ind": t.export_ind,
            }

        # 3. Build permission rows
        permission_rows: list[dict[str, Any]] = []

        for role_name, chamber_role in chamber_roles_map.items():

            role_templates = template_map.get(role_name)

            for module_code, chamber_module in chamber_modules_map.items():

                if role_templates:
                    perm = role_templates.get(module_code)
                else:
                    perm = None

                # fallback (same as your _DEFAULT_PERMISSION)
                if not perm:
                    perm = {
                        "allow_all_ind": False,
                        "read_ind": True,
                        "write_ind": False,
                        "create_ind": False,
                        "delete_ind": False,
                        "import_ind": False,
                        "export_ind": False,
                    }

                permission_rows.append({
                    "role_id": chamber_role.role_id,
                    "chamber_module_id": chamber_module.chamber_module_id,
                    "created_by": user_id,
                    **perm,
                })

        # 4. Bulk insert
        await self.role_permission_repo.bulk_create(
            session=self.session,
            data_list=permission_rows
        )    

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
 
    # ─────────────────────────────────────────────────────────────────────────
    # USERS ADD
    # ─────────────────────────────────────────────────────────────────────────

    async def users_add(self, payload: UserCreateBasic) -> str:
        email: str = payload.email or ""
        first_name: str = payload.first_name or ""
        last_name: str | None = (payload.last_name or "").strip() or None
        password: str = generate_password()
        payload.password = password

        # ── 1. VALIDATION ─────────────────────────────────────────────────────
        await self._validate_user_payload(payload, is_edit=False)

        # ── 2. CHECK MEMBERSHIP ───────────────────────────────────────────────
        membership = await self._check_user_chamber_membership(email)

        if membership["exists"]:
            if membership["deleted_ind"] or not membership["status_ind"]:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="Email already registered but not active. Try Reset Profile to activate the user.",
                )
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Email already registered. If you forgot your password, try Forgot Password.",
            )

        # ── 3. CREATE USER ────────────────────────────────────────────────────
        user = await self.users_repo.create(
            session=self.session,
            data={
                "email": email.lower(),
                "first_name": first_name.strip(),
                "last_name": last_name,
                "password_hash": hash_password(password),
                "status_ind": False,
            },
        )

        # ── 4. CREATE CHAMBER ─────────────────────────────────────────────────
        chamber = await self.chamber_repo.create(
            session=self.session,
            data={
                "chamber_name": self.get_initials(first_name, last_name),
                "email": email.lower(),
                "plan_code": RefmPlanTypesConstants.FREE,
            },
        )

        # ── 5. CREATE CHAMBER LINK ────────────────────────────────────────────
        link = await self.user_chamber_link_repo.create(
            session=self.session,
            data={
                "user_id": user.user_id,
                "chamber_id": chamber.chamber_id,
                "left_date": None,
                "status_ind": True,
                "primary_ind": True,
            },
        )

        # ── 6-9. MODULES / ROLES / PERMISSIONS ───────────────────────────────
        await self._setup_chamber_security(
            chamber_id=chamber.chamber_id,
            user_id=user.user_id,
            user_chamber_link_id=link.link_id,
        )

        # ── 10. ACTIVATION EMAIL ──────────────────────────────────────────────
        link_url = await self.email_link_service.generate_link(
            user_id=user.user_id,
            email=user.email,
            template_code=RefmEmailTemplatesEnum.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION,
        )

        return f"User created successfully. Check email for activation link: {link_url}"
 
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
 
    async def users_reset(self, link_id: str) -> dict[str, str]:

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
        
        await self.email_link_service.consume_link(encrypted_id=link_id)
        ret_value = {
            "email": email,
            "msg":"Password Changed Sussessfully, relogin"
        }
        return ret_value
 
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
 
    async def users_new_password(self, link_id: str,payload: UserPasswordIn) -> dict[str, str]:

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
        
        await self.email_link_service.consume_link(encrypted_id=link_id)
        ret_value = {
            "email": email,
            "msg":"Password Changed Sussessfully, relogin"
        }
        return ret_value

