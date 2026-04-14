"""chamber_service.py — Business logic for the Chamber / Settings module"""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber import Chamber
from app.database.models.chamber_modules import ChamberModules
from app.database.models.refm_modules import RefmModulesConstants
from app.database.models.refm_plan_types import RefmPlanTypesConstants
from app.database.repositories.chamber_modules_repository import ChamberModulesRepository
from app.database.repositories.chamber_repository import ChamberRepository
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.database.repositories.role_permission_master_repository import RolePermissionMasterRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.user_roles_repository import UserRolesRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.chamber_dto import ChamberAddAdditional, ChamberEdit, ChamberOut
from app.services.base.secured_base_service import BaseSecuredService
from app.validators import aggregate_errors
from app.validators.error_codes import ErrorCodes
from app.validators.field_validations import FieldValidator
from app.validators.validation_errors import ValidationErrorDetail

class ChamberService(BaseSecuredService):
    """Service for reading and editing the authenticated user's chamber."""

    def __init__(
            self, 
            session: AsyncSession,                 
            chamber_repo: Optional[ChamberRepository] = None,
            users_repo: Optional[UsersRepository] | None = None,
            user_chamber_link_repo: Optional[UserChamberLinkRepository] | None = None,
            chamber_module_repo: Optional[ChamberModulesRepository] = None,
            security_role_repo: Optional[SecurityRolesRepository] = None,
            chamber_role_repo: Optional[ChamberRolesRepository] = None,
            user_role_repo: Optional[UserRolesRepository] = None,
            role_permission_master_repo: Optional[RolePermissionMasterRepository] = None,
            role_permission_repo: Optional[RolePermissionsRepository] = None,
        ) -> None:
        super().__init__(session=session)
        self.chamber_repo = chamber_repo or ChamberRepository()
        self.users_repo = users_repo or UsersRepository()
        self.user_chamber_link_repo = user_chamber_link_repo or UserChamberLinkRepository()
        self.chamber_module_repo: ChamberModulesRepository = chamber_module_repo or ChamberModulesRepository()
        self.security_role_repo: SecurityRolesRepository = security_role_repo or SecurityRolesRepository()
        self.chamber_role_repo: ChamberRolesRepository = chamber_role_repo or ChamberRolesRepository()
        self.user_role_repo: UserRolesRepository = user_role_repo or UserRolesRepository()
        self.role_permission_master_repo: RolePermissionMasterRepository = role_permission_master_repo or RolePermissionMasterRepository()
        self.role_permission_repo: RolePermissionsRepository = role_permission_repo or RolePermissionsRepository()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _assert_read_permission(self) -> None:
        """Raise 403 if the logged-in user lacks read rights on SETT."""
        user = self.userDetails
        # admin_ind bypasses module-level permission checks
        if user.role and user.role.admin_ind:
            return
        
        if await self.__is_own_chamber():
            return

        perm = next(
            (p for p in user.permissions if p.module_code == RefmModulesConstants.SETTINGS),
            None,
        )
        if not perm or not (perm.read_ind or perm.allow_all_ind):
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message="You do not have permission to view Settings",
            )

    async def _assert_write_permission(self) -> None:
        """Raise 403 if the logged-in user lacks write rights on SETT."""
        user = self.userDetails
        if user.role and user.role.admin_ind:
            return
        
        if await self.__is_own_chamber():
            return

        perm = next(
            (p for p in user.permissions if p.module_code == RefmModulesConstants.SETTINGS),
            None,
        )
        if not perm or not (perm.write_ind or perm.allow_all_ind):
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message="You do not have permission to edit Settings",
            )

    async def _get_chamber(self) -> Chamber:
        """Fetch chamber scoped to the authenticated chamber_id."""
        chamber = await self.chamber_repo.get_by_id(
            session=self.session,
            filters={Chamber.chamber_id: self.chamber_id},
        )
        if not chamber:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Chamber not found",
            )
        return chamber
    
    async def _to_out(self, chamber: Chamber) -> ChamberOut:

        chamber_own = await self.__is_own_chamber()
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
            self_owned_ind = True if chamber_own else False,
        )

    async def __is_own_chamber(self):
        chamber_own  = await self.chamber_repo.get_by_id(
            session=self.session,
            filters={Chamber.created_by: self.user_id}
        )
        
        return chamber_own

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
    
    async def chamber_create(self, payload: ChamberAddAdditional, user_id:str):
                
        email: str = payload.email or ""

        # ── 4. CREATE CHAMBER ─────────────────────────────────────────────────
        chamber = await self.chamber_repo.create(
            session=self.session,
            data={
                "chamber_name": payload.chamber_name,
                "email": email.lower(),
                "plan_code": RefmPlanTypesConstants.FREE,
                "created_by": user_id,
            },
        )

        # ── 5. CREATE CHAMBER LINK ────────────────────────────────────────────
        link = await self.user_chamber_link_repo.create(
            session=self.session,
            data={
                "user_id": user_id,
                "chamber_id": chamber.chamber_id,
                "left_date": None,
                "status_ind": True,
                "primary_ind": True,
            },
        )

        # ── 6-9. MODULES / ROLES / PERMISSIONS ───────────────────────────────
        await self._setup_chamber_security(
            chamber_id=chamber.chamber_id,
            user_id=user_id,
            user_chamber_link_id=link.link_id,
        )

        return chamber

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chamber_get_by_id(self) -> ChamberOut:
        """
        GET /settings/chamber/{chamber_id}

        Guards:
          - Requested chamber_id must match the session's chamber_id.
          - User must have SETT read permission.
        """

        # 2. Permission check
        # await self._assert_read_permission()

        # 3. Fetch & return
        chamber = await self._get_chamber()
        return await self._to_out(chamber)

    async def chamber_add(self) -> ChamberOut:
        """
        POST /settings/chamber

        Guards:
          - Requested chamber_id must match the session's chamber_id.
          - User must have SETT write permission.

        Editable fields:
          chamber_name, email, phone,
          address_line1, address_line2, city, state_code, postal_code, country_code

        NOT editable here (managed by billing):
          plan_code, subscription_start, subscription_end, status_ind
        """

        chamber_own  = await self.chamber_repo.get_by_id(
            session=self.session,
            filters={Chamber.created_by: self.user_id}
        )
        if chamber_own:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Chamber Already exists for user",
            )        
        
        user = self.current_user
        chamber_payload: ChamberAddAdditional = ChamberAddAdditional(
                chamber_name= self.get_initials(user.first_name, user.last_name),
                email= user.email,
                plan_code = RefmPlanTypesConstants.FREE,
        )

        created_chamber = await self.chamber_create(payload=chamber_payload,user_id=self.user_id)

        return await self._to_out(created_chamber)

    async def chamber_edit(self, payload: ChamberEdit) -> ChamberOut:
        """
        PUT /settings/chamber/{chamber_id}/edit

        Guards:
          - Requested chamber_id must match the session's chamber_id.
          - User must have SETT write permission.

        Editable fields:
          chamber_name, email, phone,
          address_line1, address_line2, city, state_code, postal_code, country_code

        NOT editable here (managed by billing):
          plan_code, subscription_start, subscription_end, status_ind
        """

        # 2. Permission check
        await self._assert_write_permission()

        # 3. Confirm chamber exists
        await self._get_chamber()

        # 4. Field-level validations
        errors = []

        if not payload.chamber_name:
            errors.append( ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Chamber Name is required"
            ))

        if payload.email and (err := FieldValidator.validate_email(payload.email)):
            errors.append(err)

        if payload.phone and (err := FieldValidator.validate_phone(payload.phone)):
            errors.append(err)

        if payload.state_code and len(payload.state_code.strip()) != 2:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="state_code must be a 2-character code",
                )
            )

        if payload.country_code and len(payload.country_code.strip()) != 2:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="country_code must be a 2-character code",
                )
            )

        if errors:
            aggregate_errors(errors=errors)

        # 5. Build update dict — only fields explicitly supplied in the request
        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        if not data:
            # Nothing to update; return current state
            chamber = await self._get_chamber()
            return await self._to_out(chamber)

        # Stamp who last updated
        data["updated_by"] = self.user_id

        updated_chamber = await self.chamber_repo.update(
            session=self.session,
            filters={Chamber.chamber_id: self.chamber_id},
            data=self.chamber_repo.map_fields_to_db_column(data),
        )

        return await self._to_out(updated_chamber)