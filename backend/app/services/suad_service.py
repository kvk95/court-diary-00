# app/services/suad_service.py

from collections.abc import Iterable
from datetime import datetime, timezone
import re
from typing import Any, Callable, Dict, Optional, List, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.runtime_settings import set_runtime_settings
from app.database.models.activity_log import ActivityLog
from app.database.models.refm_announcement_status import RefmAnnouncementStatusConstants
from app.database.models.security_roles import SecurityRoles
from app.database.models.users import Users
from app.database.repositories.activity_log_repository import ActivityLogRepository
from app.database.repositories.announcements_repository import AnnouncementsRepository
from app.database.repositories.chamber_modules_repository import ChamberModulesRepository
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.database.repositories.global_settings_repository import GlobalSettingsRepository
from app.database.repositories.role_permission_master_repository import RolePermissionMasterRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.suad_repository import SuadRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import RecentActivityItem
from app.dtos.suad_dto import (
    AnnouncementBaseIn,
    AnnouncementCreate,
    AnnouncementOut,
    AnnouncementUpdate,
    ChamberItem,
    ChamberStatsOut,
    GlobalSettingsEdit,
    GlobalSettingsOut,
    PermissionCloneIn,
    PermissionCloneOut,
    PermissionPushIn,
    MasterRolePermissionDetail,
    MasterRolePermissionStats,
    PermissionUpdateIn,
    SecurityRoleBaseIn,
    SecurityRoleCreate,
    SecurityRoleItem,
    SecurityRoleStats,
    SecurityRoleUpdate,
    SuperAdminDashboardStats,
    TopChamberItem,
    UserItem,
    UserStatsOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.activity_formatter import format_activity
from app.utils.utilities import decode_text, encode_text, ensure_utc
from app.validators import aggregate_errors
from app.validators.error_codes import ErrorCodes
from app.validators.field_validations import FieldValidator
from app.validators.validation_errors import ValidationErrorDetail


class SuadService(BaseSecuredService):
    """
    Super Admin Service Layer
    """

    def __init__(
        self,
        session: AsyncSession,
        suad_repo: Optional[SuadRepository] = None,
        global_settings_repo: Optional[GlobalSettingsRepository] = None,
        announcement_repo: Optional[AnnouncementsRepository] = None,
        security_roles_repo: Optional[SecurityRolesRepository] = None,
        chamber_roles_repo: Optional[ChamberRolesRepository] = None,
        role_permission_master_repo: Optional[RolePermissionMasterRepository] = None,
        chamber_modules_repo: Optional[ChamberModulesRepository] = None,
        role_permissions_repo: Optional[RolePermissionsRepository] = None,
        activity_log_repo: Optional[ActivityLogRepository] = None,
    ):
        super().__init__(session)
        self.suad_repo = suad_repo or SuadRepository()
        self.global_settings_repo = global_settings_repo or GlobalSettingsRepository()
        self.announcement_repo = announcement_repo or AnnouncementsRepository()
        self.security_roles_repo = security_roles_repo or SecurityRolesRepository()
        self.chamber_roles_repo = chamber_roles_repo or ChamberRolesRepository()
        self.role_permission_master_repo = role_permission_master_repo or RolePermissionMasterRepository()
        self.chamber_modules_repo = chamber_modules_repo or ChamberModulesRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()
        self.activity_log_repo = activity_log_repo or ActivityLogRepository()

    # ---------------------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------------------

    K = TypeVar("K")
    V = TypeVar("V")

    async def _load_map(
        self,
        ids: Iterable[K],
        query_builder: Callable[[list[K]], Any],
        key_fn: Callable[[Any], K],
        value_fn: Callable[[Any], V],
    ) -> Dict[K, V]:
        ids = list({i for i in ids if i})
        if not ids:
            return {}
        rows = (await self.session.execute(query_builder(ids))).all()
        return {key_fn(r): value_fn(r) for r in rows}

    # ---------------------------------------------------------------------
    # GLOBAL SETTINGS
    # ---------------------------------------------------------------------
    async def get_settings(self) -> GlobalSettingsOut:

        row = await self.global_settings_repo.get_first(session=self.session)

        if not row:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Settings not Found")

        return self._to_out_gset(row)

    def _to_out_gset(self, row):
        return GlobalSettingsOut(
            # branding
            platform_name=row.platform_name,
            company_name=row.company_name,
            support_email=row.support_email,
            primary_color=row.primary_color,
            # smtp
            smtp_host=row.smtp_host,
            smtp_user_name=decode_text(row.smtp_user_name) if row.smtp_user_name else None,
            smtp_password=decode_text(row.smtp_password) if row.smtp_password else None,
            smtp_use_tls=row.smtp_use_tls,
            smtp_port=row.smtp_port,
            # sms
            sms_provider=row.sms_provider,
            sms_api_key=decode_text(row.sms_api_key) if row.sms_api_key else None,
            # maintenance
            maintenance_enabled=row.maintenance_enabled if row.maintenance_enabled != None else False,
            maintenance_start=row.maintenance_start,
            maintenance_end=row.maintenance_end,
            # feature flags
            allow_user_registration=row.allow_user_registration if row.allow_user_registration != None else False,
            enable_case_collaboration=row.enable_case_collaboration if row.enable_case_collaboration != None else False,
            enable_reports_module=row.enable_reports_module if row.enable_reports_module != None else False,
            enable_api_rate_limit=row.enable_api_rate_limit if row.enable_api_rate_limit != None else False,
        )

    def _to_announcement_out(self, row):        
        return AnnouncementOut(
            announcement_id = row.announcement_id,
            title = row.title,
            content = row.content,
            type_code = row.announcement_id,
            audience_code = row.audience_code,
            status_code = row.status_code,
            scheduled_at = row.scheduled_at,
            expires_at = row.expires_at,
            created_date = row.created_date,
        )
    
    def _to_roles_out(self, row: dict[str, Any] | None):
        if not row:
            raise ValidationErrorDetail(code=ErrorCodes.NOT_FOUND, message="Role not Found")

        return SecurityRoleItem(**row);

    def __to_permissions_out(self, rows):
        return [
            MasterRolePermissionDetail(
                permission_id = r.id,
                module_code = r.module_code,
                module_name = r.module_name,
                allow_all_ind = r.allow_all_ind,
                read_ind = r.read_ind,
                write_ind = r.write_ind,
                create_ind = r.create_ind,
                delete_ind = r.delete_ind,
                import_ind = r.import_ind,
                export_ind = r.export_ind,
            )
            for r in rows
        ]
    
    async def __bulk_upsert_role_permission(
        self,
        session,
        rows: list[dict],
    ):
        return await self.role_permission_master_repo.bulk_upsert(
            session=session,
            rows=rows,

            unique_columns=[
                "role_id",
                "chamber_module_id",
            ],

            update_columns=[
                "allow_all_ind",

                "read_ind",
                "write_ind",
                "create_ind",
                "delete_ind",

                "import_ind",
                "export_ind",

                "updated_by",
                "updated_date",
            ]
        )
    
    def _resolve_status(self, payload, now: datetime) -> str:
        # publish override
        if getattr(payload, "publish_now", False):
            return RefmAnnouncementStatusConstants.ACTIVE

        scheduled_at = getattr(payload, "scheduled_at", None)
        expires_at = getattr(payload, "expires_at", None)

        if scheduled_at and scheduled_at > now:
            return RefmAnnouncementStatusConstants.SCHEDULED

        if expires_at and expires_at <= now:
            return RefmAnnouncementStatusConstants.EXPIRED

        return RefmAnnouncementStatusConstants.DRAFT
    
    def _err(self, msg: str):
        return ValidationErrorDetail(
            code=ErrorCodes.VALIDATION_ERROR,
            message=msg
        )

    # -----------------------------
    # EDIT (protected)
    # -----------------------------
    async def update_settings(self, payload: GlobalSettingsEdit) -> GlobalSettingsOut:

        errors = []
        # -----------------------------
        # 📧 Email
        # -----------------------------
        if payload.support_email:
            if err := FieldValidator.validate_email(payload.support_email):
                errors.append(err)

        # -----------------------------
        # 🎨 Color (hex validation)
        # -----------------------------
        if payload.primary_color:
            if not re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", payload.primary_color):
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Invalid hex color code"
                    )
                )

        # -----------------------------
        # 📧 SMTP Validation
        # -----------------------------
        # validate individual fields
        if payload.smtp_port is not None:
            if not (1 <= payload.smtp_port <= 65535):
                errors.append(ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,message="Invalid SMTP port"))

        if payload.smtp_user_name:
            if "@" not in payload.smtp_user_name:
                errors.append(ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,message="Invalid SMTP username/email"))

        # -----------------------------
        # 📱 SMS Validation
        # -----------------------------
        if payload.sms_provider and not payload.sms_api_key:
            errors.append(
                ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,message="SMS API key required for provider")
            )

        if payload.sms_api_key and len(payload.sms_api_key) < 10:
            errors.append(
                ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,message="Invalid SMS API key")
            )

        # -----------------------------
        # ⚙️ Maintenance Validation
        # -----------------------------
        if payload.maintenance_start and payload.maintenance_end:
            if payload.maintenance_start >= payload.maintenance_end:
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Maintenance start must be before end"
                    )
                )

        # Optional: prevent past scheduling
        now = datetime.now(timezone.utc)

        if payload.maintenance_start and payload.maintenance_start < now:
            errors.append(
                ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                    message="Maintenance start cannot be in the past"
                )
            )

        if errors:
            aggregate_errors(errors=errors)
            
        row = await self.global_settings_repo.get_first(session=self.session)

        if not row:
            raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="Settings not Found")

        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        if "sms_api_key" in data:
            data["sms_api_key"] = encode_text(data["sms_api_key"]) 

        if "smtp_password" in data:
            data["smtp_password"] = encode_text(data["smtp_password"]) 

        if "smtp_user_name" in data:
            data["smtp_user_name"] = encode_text(data["smtp_user_name"]) 

        updated = await self.global_settings_repo.update(
            session=self.session,
            data=data,
            id_values=row.settings_id
        )

        set_runtime_settings({
            "SMTP_SERVER": updated.smtp_host,
            "SMTP_SERVER_PORT": updated.smtp_port,
            "SMTP_SERVER_USERNAME": updated.smtp_user_name,
            "SMTP_SERVER_PASSWORD": updated.smtp_password,
            "SMTP_USE_TLS": updated.smtp_use_tls,
        })

        return self._to_out_gset(updated)

    # ---------------------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------------------
    async def get_superadmin_dashboard(self,
                                       search: str | None = None,
                                       ) -> List[TopChamberItem]:
        """
        Main Super Admin Dashboard
        """

        # --- Top Chambers ---
        top_chambers_raw = await self.suad_repo.get_top_chambers_by_cases(
            session=self.session,
            search=search,
        )

        top_chambers: List[TopChamberItem] = [
            TopChamberItem(**item) for item in top_chambers_raw
        ]

        return top_chambers
    
    async def get_dashboard_stats(self) -> SuperAdminDashboardStats:
        """
        Main Super Admin Dashboard Stats
        """

        now = datetime.now(timezone.utc)

        # --- Core Stats ---
        stats = await self.suad_repo.get_dashboard_stats(
            session=self.session,
            today=now.date(),
        )

        return SuperAdminDashboardStats(
            total_chambers=stats["total_chambers"],
            total_users=stats["total_users"],
            active_cases=stats["active_cases"],
            active_subscriptions=stats["active_subscriptions"],
            monthly_revenue=stats["monthly_revenue"],
            system_health=stats["system_health"],
        )


    async def get_recent_activity(
        self,
        limit: int = 10
    ) -> List[RecentActivityItem]:

        try:
            rows = await self.session.execute(
                select(
                    ActivityLog.action,
                    ActivityLog.actor_user_id,
                    ActivityLog.created_date,
                    ActivityLog.metadata_json,
                )
                # ✅ NO chamber filter (SUAD)
                .order_by(ActivityLog.created_date.desc())
                .limit(limit)
            )
            activity_rows = rows.fetchall()

        except Exception:
            return []

        # -------------------------------------------------------
        # 🔥 SAME batching logic (reuse your pattern)
        # -------------------------------------------------------
        actor_ids = [r.actor_user_id for r in activity_rows if r.actor_user_id]

        actor_map = await self._load_map(
            actor_ids,
            lambda ids: select(
                Users.user_id,
                Users.first_name,
                Users.last_name,
            ).where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: self.full_name(r.first_name, r.last_name),
        )

        # -------------------------------------------------------
        # 🔥 SAME formatter (no change)
        # -------------------------------------------------------
        return [
            format_activity(
                log=r,
                actor_name=actor_map.get(r.actor_user_id) if r.actor_user_id else "System",
            )
            for r in activity_rows
        ]
    
    async def get_chambers(
        self,
        page: int,
        limit: int,
        search: str | None,
        status: str | None,
    ) -> PagingData[ChamberItem]:

        items_raw, total = await self.suad_repo.list_chambers(
            session=self.session,
            page=page,
            limit=limit,
            search=search,
            status=status,
        )

        records = [ChamberItem(**i) for i in items_raw]

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit
        ).build(records=records)
    
    async def get_chambers_stats(
        self,
    ) -> ChamberStatsOut:

        stats = await self.suad_repo.get_stats(self.session)

        stats=ChamberStatsOut(**stats)

        return stats
    
    async def get_users(
        self,
        page: int,
        limit: int,
        search: str | None,
        status: str | None,
    ) -> PagingData[UserItem]:

        items_raw, total = await self.suad_repo.list_users(
            session=self.session,
            page=page,
            limit=limit,
            search=search,
            status=status,
        )

        records = [UserItem(**i) for i in items_raw]

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit
        ).build(records=records)
    
    async def get_user_stats(
        self,
    ) -> UserStatsOut:

        stats = await self.suad_repo.get_user_stats(self.session)

        return (UserStatsOut(**stats))

    # ---------------------------------------------------------------------
    # announcements
    # ---------------------------------------------------------------------

    async def get_announcements(
        self,
        page: int,
        limit: int,
        search: str | None,
        status: str | None,
        type_code: str | None,
        audience_code: str | None,
    ) -> PagingData[AnnouncementOut]:

        rows, total = await self.announcement_repo.list_announcements(
            session=self.session,
            page=page,
            limit=limit,
            search=search,
            status=status,
            type_code=type_code,
            audience_code=audience_code,
        )

        records = [self._to_announcement_out(row) for row in rows]

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit,
        ).build(records=records)
    
    async def get_announcement(self, announcement_id: str):
        row = await self.announcement_repo.get_by_id(
            session=self.session,
            id_values=announcement_id
        )

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Announcement not found"
            )

        return self._to_announcement_out(row)

    async def create_announcement(self, payload: AnnouncementCreate) -> AnnouncementOut:

        now = datetime.now(timezone.utc)
        errors = []

        # Normalize payload datetimes BEFORE comparison
        scheduled_at = ensure_utc(payload.scheduled_at)
        expires_at = ensure_utc(payload.expires_at)

        # ---------------- VALIDATIONS ----------------
        if not payload.title or not payload.title.strip():
            errors.append(self._err("title is required"))

        if scheduled_at and scheduled_at < now:
            errors.append(self._err("scheduled_at cannot be in the past"))

        if scheduled_at and expires_at:
            if scheduled_at >= expires_at:
                errors.append(self._err("scheduled_at must be before expires_at"))

        if expires_at and expires_at <= now:
            errors.append(self._err("expires_at must be in future"))

        if errors:
            aggregate_errors(errors)

        # ---------------- STATUS ----------------
        status = self._resolve_status(payload, now)

        # ---------------- DATA ----------------
        data = payload.model_dump(exclude_unset=True)

        data["status_code"] = status
        data["created_by"] = self.user_id
        if getattr(payload, "publish_now", False):
            data.pop("publish_now")

        created = await self.announcement_repo.create(
            session=self.session,
            data=data
        )

        return self._to_announcement_out(created)
    
    async def update_announcement(
        self,
        payload: AnnouncementUpdate
    ) -> AnnouncementOut:
        
        announcement_id = payload.announcement_id

        now = datetime.now(timezone.utc)

        row = await self.announcement_repo.get_by_id(
            session=self.session,
            id_values=announcement_id
        )

        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Announcement not found"
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        errors = []

        # ---------------- VALIDATIONS ----------------

        if "title" in data and not data["title"].strip():
            errors.append(self._err("title cannot be empty"))

        scheduled_at = data.get("scheduled_at", row.scheduled_at)
        expires_at = data.get("expires_at", row.expires_at)       

        # Normalize payload datetimes BEFORE comparison
        scheduled_at = ensure_utc(scheduled_at)
        expires_at = ensure_utc(expires_at)

        if scheduled_at and scheduled_at < now:
            errors.append(self._err("scheduled_at cannot be in the past"))

        if scheduled_at and expires_at:
            if scheduled_at >= expires_at:
                errors.append(self._err("scheduled_at must be before expires_at"))

        if errors:
            aggregate_errors(errors)

        # ---------------- STATUS RECALC ----------------

        status = self._resolve_status(
            payload=payload,
            now=now
        )

        data["status_code"] = status
        data["updated_by"] = self.user_id
        if getattr(payload, "publish_now", False):
            data.pop("publish_now")

        updated = await self.announcement_repo.update(
            session=self.session,
            data=data,
            id_values=announcement_id
        )

        return self._to_announcement_out(updated)
    
    async def delete_announcement(self,  payload: AnnouncementBaseIn):
        announcement_id = payload.announcement_id
        await self.announcement_repo.delete(
            session=self.session,
            id_values=announcement_id,
        )
        return {"announcement_id": announcement_id, "deleted": True}

    # ---------------------------------------------------------------------
    # SECURITY ROLES
    # ---------------------------------------------------------------------

    async def get_security_role_stats(self) -> SecurityRoleStats:
        
        stats = await self.security_roles_repo.get_role_stats(session=self.session)

        return SecurityRoleStats(**stats)
    
    async def get_security_roles(self, page, limit, search) -> PagingData[SecurityRoleItem]:

        items_raw, total = await self.security_roles_repo.list_roles(
            session=self.session,
            page=page,
            limit=limit,
            search=search,
        )
        records = [self._to_roles_out(row) for row in items_raw]

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit
        ).build(records=records)
    
    async def create_security_role(self, payload: SecurityRoleCreate) -> SecurityRoleItem:

        if not payload.role_code or not payload.role_code.strip():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role code is required"
            )

        if not payload.role_name or not payload.role_name.strip():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role name is required"
            )

        role_code = payload.role_code.strip()
        role_name = payload.role_name.strip()

        # ✅ Active duplicate check
        existing = await self.security_roles_repo.get_first(
            self.session,
            where=[
                SecurityRoles.deleted_ind.is_(False),
                or_(
                    SecurityRoles.role_code == role_code,
                    SecurityRoles.role_name == role_name,
                ),
            ],
        )

        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role code '{role_code}' or Role name '{role_name}' already exists",
            )

        # ✅ Check soft-deleted duplicate
        stmt = select(SecurityRoles).where(
            or_(
                SecurityRoles.role_code == role_code,
                SecurityRoles.role_name == role_name,
            )
        )

        result = await self.session.execute(stmt)
        soft_deleted = result.scalars().first()

        if soft_deleted and soft_deleted.deleted_ind:
            # 🔥 REVIVE
            revived = await self.security_roles_repo.update(
                session=self.session,
                id_values=soft_deleted.role_id,
                data={
                    "deleted_ind": False,
                    "role_name": role_name,
                    "role_code": role_code,
                    "description": payload.description,
                    "status_ind": True,
                }
            )

            row = await self.security_roles_repo.get_by_role_id(self.session, revived.role_id)
            return self._to_roles_out(row)

        # ✅ CREATE
        role = await self.security_roles_repo.create(
            session=self.session,
            data={
                "role_code": role_code,
                "role_name": role_name,
                "description": payload.description,
                "admin_ind": payload.admin_ind or False,
                "system_ind": payload.system_ind or False,
                "status_ind": True,
                "created_by": self.user_id,
            }
        )

        row = await self.security_roles_repo.get_by_role_id(self.session, role.role_id)
        return self._to_roles_out(row)
    
    async def update_security_role(self, payload: SecurityRoleUpdate) -> SecurityRoleItem:

        role_id = payload.role_id

        existing = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
            include_chamber_id=False,
        )

        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Role not found"
            )

        if existing.admin_ind:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Protected role cannot be modified"
            )

        update_data = {}

        # 🔹 ROLE NAME UPDATE
        if payload.role_name and payload.role_name.strip():
            new_name = payload.role_name.strip()

            # Active duplicate check
            duplicate = await self.security_roles_repo.get_first(
                self.session,
                where=[
                    SecurityRoles.role_name == new_name,
                    SecurityRoles.role_id != role_id,
                    SecurityRoles.deleted_ind.is_(False),
                ],
            )

            if duplicate:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name '{new_name}' already exists"
                )

            # Soft-deleted duplicate
            stmt = select(SecurityRoles).where(
                SecurityRoles.role_name == new_name,
                SecurityRoles.role_id != role_id,
                SecurityRoles.deleted_ind.is_(True)
            )

            result = await self.session.execute(stmt)
            soft_deleted = result.scalars().first()

            if soft_deleted:
                # 🔥 REVIVE INSTEAD
                revived = await self.security_roles_repo.update(
                    session=self.session,
                    id_values=soft_deleted.role_id,
                    data={
                        "deleted_ind": False,
                        "role_name": new_name,
                        "description": payload.description,
                        "status_ind": payload.status_ind if payload.status_ind is not None else True,
                    }
                )

                row = await self.security_roles_repo.get_by_role_id(self.session, revived.role_id)
                return self._to_roles_out(row)

            update_data["role_name"] = new_name

        # 🔹 OTHER FIELDS
        if payload.description is not None:
            update_data["description"] = payload.description

        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        if not update_data:
            row = await self.security_roles_repo.get_by_role_id(self.session, role_id)
            return self._to_roles_out(row)

        updated = await self.security_roles_repo.update(
            session=self.session,
            data=update_data,
            id_values=role_id
        )

        row = await self.security_roles_repo.get_by_role_id(self.session, updated.role_id)
        return self._to_roles_out(row)
    
    async def delete_security_role(self, payload: SecurityRoleBaseIn) -> dict:

        role_id = payload.role_id

        role = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
            include_chamber_id=False,
        )

        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Role not found"
            )

        if role.admin_ind:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Protected role cannot be deleted"
            )

        # 🔥 CHECK USAGE IN CHAMBERS
        in_use = await self.chamber_roles_repo.exists_in_chambers(
            session=self.session,
            role_id=role_id
        )

        if in_use:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role is used in chambers"
            )

        await self.security_roles_repo.delete(
            session=self.session,
            id_values=role_id,
            soft=True
        )

        return {
            "role_id": role_id,
            "deleted": True
        }

    # ---------------------------------------------------------------------
    # ROLES PERMISSION MASTER
    # ---------------------------------------------------------------------

    async def get_permission_stats(self) -> MasterRolePermissionStats:

        row = await self.role_permission_master_repo.get_last_updated(self.session)
        
        return MasterRolePermissionStats(
            total_templates=await self.security_roles_repo.count(self.session),

            modules_covered=await self.role_permission_master_repo.count_distinct_modules(self.session),
            

            last_pushed= row.last_pushed if row else None
        )
    
    async def get_permission_detail(self, role_id: int) -> List[MasterRolePermissionDetail]:

        rows = await self.role_permission_master_repo.get_by_role(
            self.session,
            role_id
        )

        return self.__to_permissions_out(rows)
    
    async def clone_permission(self, payload: PermissionCloneIn) -> PermissionCloneOut:

        new_role:SecurityRoleItem = await self.create_security_role(payload)

        for p in payload.permissions:

            permission = await self.role_permission_master_repo.create(
                session=self.session,
                data={
                    "security_role_id": new_role.role_id,

                    "module_code": p.module_code,

                    "allow_all_ind": p.allow_all_ind,

                    "read_ind": p.read_ind,
                    "write_ind": p.write_ind,
                    "create_ind": p.create_ind,
                    "delete_ind": p.delete_ind,

                    "import_ind": p.import_ind,
                    "export_ind": p.export_ind,
                }
            )
            
        rows = await self.role_permission_master_repo.get_by_role(
            self.session,
            new_role.role_id
        )

        permissions_out = self.__to_permissions_out(rows)
        out:PermissionCloneOut = PermissionCloneOut(
            role_id = new_role.role_id,
            role_code= new_role.role_code,
            role_name= new_role.role_name,
            description= new_role.description,
            system_ind= new_role.system_ind,
            admin_ind= new_role.admin_ind,
            permissions = permissions_out
        )

        return out
    
    async def update_permission(self, payload: PermissionUpdateIn) -> PermissionCloneOut:

        role = await self.security_roles_repo.get_by_id(
            self.session,
            id_values=payload.role_id,
        )

        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="Role not found"
            )

        for p in payload.permissions:

            permission = await self.role_permission_master_repo.upsert(
                session=self.session,
                id_values=p.permission_id,
                data={
                    "security_role_id": payload.role_id,

                    "module_code": p.module_code,

                    "allow_all_ind": p.allow_all_ind,

                    "read_ind": p.read_ind,
                    "write_ind": p.write_ind,
                    "create_ind": p.create_ind,
                    "delete_ind": p.delete_ind,

                    "import_ind": p.import_ind,
                    "export_ind": p.export_ind,
                }
            )
            
        rows = await self.role_permission_master_repo.get_by_role(
            self.session,
            role.role_id
        )

        permissions_out = self.__to_permissions_out(rows)

        out:PermissionCloneOut = PermissionCloneOut(
            role_id = role.role_id,
            role_code= role.role_code,
            role_name= role.role_name,
            description= role.description,
            system_ind= role.system_ind,
            admin_ind= role.admin_ind,
            permissions = permissions_out
        )

        return out
    
    async def push_permission(self, payload: PermissionPushIn):

        perms = await self.role_permission_master_repo.get_by_role(
            self.session,
            payload.role_id
        )

        chamber_roles = await self.chamber_roles_repo.get_by_security_role(
            self.session,
            payload.role_id
        )

        bulk_rows = []

        for cr in chamber_roles:

            module_map = await self.chamber_modules_repo.get_modules_by_chamber(
                self.session,
                cr.chamber_id
            )

            for p in perms:

                chamber_module_id = module_map.get(p.module_code)

                if not chamber_module_id:
                    continue

                bulk_rows.append({
                    "role_id": cr.role_id,
                    "chamber_module_id": chamber_module_id,

                    "allow_all_ind": p.allow_all_ind,

                    "read_ind": p.read_ind,
                    "write_ind": p.write_ind,
                    "create_ind": p.create_ind,
                    "delete_ind": p.delete_ind,

                    "import_ind": p.import_ind,
                    "export_ind": p.export_ind,

                    "updated_by": self.user_id,
                })

        await self.__bulk_upsert_role_permission(
            session=self.session,
            rows=bulk_rows,
        )

        return {
            "updated": True,
            "total": len(bulk_rows),
        }

    async def get_recent_activity_paged(
        self, 
        page: int,
        limit: int,
    ) -> PagingData[RecentActivityItem]:
        activity_rows, total = await self.activity_log_repo.get_all_chamber_recent_activity_paged(
            session=self.session,
            page=page,
            limit=limit)
        # Load actor names efficiently
        actor_ids = [r.actor_user_id for r in activity_rows if r.actor_user_id]
        actor_map = await self._load_map(
            actor_ids,
            lambda ids: select(
                Users.user_id,
                Users.first_name,
                Users.last_name,
            ).where(Users.user_id.in_(ids)),
            lambda r: r.user_id,
            lambda r: self.full_name(r.first_name, r.last_name),
        )

        recent_activities = [
            format_activity(
                log=r,
                actor_name=actor_map.get(r.actor_user_id) if r.actor_user_id else "System",
            )
            for r in activity_rows
        ]

        return PagingBuilder(
            total_records=total,
            page=page,
            limit=limit,
        ).build(records=recent_activities)