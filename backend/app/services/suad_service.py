# app/services/suad_service.py

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, List, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.activity_log import ActivityLog
from app.database.models.users import Users
from app.database.repositories.suad_repository import SuadRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.cases_dto import RecentActivityItem
from app.dtos.suad_dto import (
    ChamberItem,
    ChamberStatsOut,
    SuperAdminDashboardOut,
    SuperAdminDashboardStats,
    TopChamberItem,
    UserItem,
    UserStatsOut,
)
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.activity_formatter import format_activity


class SuadService(BaseSecuredService):
    """
    Super Admin Service Layer
    """

    def __init__(
        self,
        session: AsyncSession,
        suad_repo: Optional[SuadRepository] = None,
    ):
        super().__init__(session)
        self.suad_repo = suad_repo or SuadRepository()

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
    # DASHBOARD
    # ---------------------------------------------------------------------
    async def get_superadmin_dashboard(self,
                                       limit: int,
                                       search: str | None = None,
                                       ) -> SuperAdminDashboardOut:
        """
        Main Super Admin Dashboard
        """

        # --- Top Chambers ---
        top_chambers_raw = await self.suad_repo.get_top_chambers_by_cases(
            session=self.session,
            search=search,
            limit=limit,
        )

        top_chambers: List[TopChamberItem] = [
            TopChamberItem(**item) for item in top_chambers_raw
        ]

        return SuperAdminDashboardOut(
            top_chambers=top_chambers,
        )
    
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