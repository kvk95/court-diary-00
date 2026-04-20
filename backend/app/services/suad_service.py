# app/services/suad_service.py

from collections.abc import Iterable
from datetime import datetime, timezone
import re
from typing import Any, Callable, Dict, Optional, List, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.runtime_settings import set_runtime_settings
from app.database.models.activity_log import ActivityLog
from app.database.models.users import Users
from app.database.repositories.global_settings_repository import GlobalSettingsRepository
from app.database.repositories.suad_repository import SuadRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import RecentActivityItem
from app.dtos.suad_dto import (
    ChamberItem,
    ChamberStatsOut,
    GlobalSettingsEdit,
    GlobalSettingsOut,
    SuperAdminDashboardStats,
    TopChamberItem,
    UserItem,
    UserStatsOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.activity_formatter import format_activity
from app.utils.utilities import decode_text, encode_text
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
    ):
        super().__init__(session)
        self.suad_repo = suad_repo or SuadRepository()
        self.global_settings_repo = global_settings_repo or GlobalSettingsRepository()

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
            raise ValidationErrorDetail(code=ErrorCodes.VALIDATION_ERROR, message="Settings not Found")

        return self._to_out(row)

    def _to_out(self, row):
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

        return self._to_out(updated)

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