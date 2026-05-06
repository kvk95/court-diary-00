# app/services/dashboard_service.py

from datetime import date, datetime, timedelta
from typing import List, Optional, Any, Callable, Dict, Iterable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.hearings import Hearings
from app.database.models.refm_modules import RefmModulesConstants
from app.database.models.users import Users
from app.database.repositories.activity_log_repository import ActivityLogRepository
from app.database.repositories.dashboard_repository import DashboardRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.dashboard_dto import (
    AdminDashboardOut,
    AdminStatCards,
    ChamberManagementStats,
    DashboardHearingItem,
    MainDashboardOut,
    OverdueCaseItem,
    PracticeOverviewStats,
    RecentActivityItem,
    SummaryCountsOut,
)
from app.dtos.role_permissions_dto import RolePermissionModuleOut
from app.dtos.roles_dto import RoleOut
from app.dtos.users_dto import UserOut
from app.services.base.secured_base_service import BaseSecuredService
from app.utils.activity_formatter import format_activity

class DashboardService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        dashboard_repo: Optional[DashboardRepository] = None,
        activity_log_repo: Optional[ActivityLogRepository] = None,
    ):
        super().__init__(session)
        self.dashboard_repo = dashboard_repo or DashboardRepository()
        self.activity_log_repo = activity_log_repo or ActivityLogRepository()

    # ===================================================================
    # HELPERS
    # ===================================================================

    def _greeting(self, hour: int) -> str:
        if hour < 12:
            return "Good morning"
        if hour < 17:
            return "Good afternoon"
        return "Good evening"

    def _trend_pct(self, current: int, previous: int) -> Optional[float]:
        """Calculate month-over-month percentage change. Returns None if previous is 0."""
        if previous == 0:
            return None
        return round(((current - previous) / previous) * 100, 1)

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

    async def _get_hearing_status_maps(self):
        """Load both description and color maps once."""
        hearing_status_maps = await self.refm_resolver.get_refm_map(column_attr=Hearings.status_code)
        return hearing_status_maps

    async def _to_hearing_item(self, r: dict, hearing_status_maps: dict) -> DashboardHearingItem:
        """Convert dict row to DashboardHearingItem DTO."""
        
        purpose_description = await self.refm_resolver.from_column(
            column_attr=Hearings.purpose_code,
            code=r.get("purpose_code"),
            value_column=RefmHearingPurpose.description,
            default=None
        )

        status_description = await self.refm_resolver.get_value_from_map(
            desc_map=hearing_status_maps,
            code=r.get("status_code"),
            value_column=RefmHearingStatus.description,
            default=None
        )

        color = await self.refm_resolver.get_value_from_map(
            desc_map=hearing_status_maps,
            code=r.get("status_code"),
            value_column=RefmHearingStatus.color_code,
            default=None
        )

        return DashboardHearingItem(
            hearing_id=r.get("hearing_id") or "",
            case_id=r.get("case_id") or "",
            case_number=r.get("case_number") or "",
            court_name=r.get("court_name") or "",
            petitioner=r.get("petitioner") or "",
            respondent=r.get("respondent") or "",
            hearing_date=r.get("hearing_date") or date.today(),
            purpose_code=r.get("purpose_code"),
            purpose_description=purpose_description,
            status_code=r.get("status_code"),
            status_description=status_description,
            color=color,
        )

    # ===================================================================
    # MAIN DASHBOARD
    # ===================================================================

    async def get_main_dashboard(self, user_first_name: str) -> MainDashboardOut:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        cid = self.chamber_id
        hour = datetime.now().hour

        # Fetch all data from repository
        overview = await self.dashboard_repo.get_practice_overview(
            session=self.session, chamber_id=cid, today=today
        )
        chamber_stats = await self.dashboard_repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid, today=today
        )
        overdue_rows = await self.dashboard_repo.get_overdue_cases(
            session=self.session, chamber_id=cid, today=today
        )
        today_rows = await self.dashboard_repo.get_hearings_for_date(
            session=self.session, chamber_id=cid, hearing_date=today
        )
        tomorrow_rows = await self.dashboard_repo.get_hearings_for_date(
            session=self.session, chamber_id=cid, hearing_date=tomorrow
        )

        hearing_status_maps = await self._get_hearing_status_maps()

        # =========================
        # EXTRACT NEW STRUCTURE
        # =========================
        cases_overview = overview["cases_overview"]
        hearings_overview = overview["hearings_overview"]
        last_hearing_purpose_map = await self.refm_resolver.get_desc_map(column_attr=Hearings.purpose_code, 
                                                                         value_column=RefmHearingPurpose.description)

        # =========================
        # Convert overdue cases
        # =========================
        overdue_cases = [
            OverdueCaseItem(
                case_id=r["case_id"],
                case_number=r["case_number"],
                court_name=r["court_name"],
                petitioner=r["petitioner"],
                respondent=r["respondent"],
                next_hearing_date=r.get("case_next_hearing_date") or r.get("next_hearing_date"),
                days_overdue=(
                    (today - (r.get("case_next_hearing_date") or r.get("next_hearing_date"))).days
                    if (r.get("case_next_hearing_date") or r.get("next_hearing_date"))
                    else 0
                ),
                last_hearing_purpose=await self.refm_resolver.get_value(
                    desc_map=last_hearing_purpose_map,
                    code=r.get("purpose_code"),
                    default=None   # better to be explicit
                ),
            )
            for r in overdue_rows
        ]

        # =========================
        # BUILD RESPONSE
        # =========================
        mainDashboardOut: MainDashboardOut = MainDashboardOut(
            greeting=self._greeting(hour),
            user_first_name=user_first_name,

            # ✅ FIXED
            active_cases_count=cases_overview["total_active_cases"],
            today_hearings_count=hearings_overview["today"]["total"],

            today=today,

            practice_overview=PracticeOverviewStats(
                active_cases=cases_overview["total_active_cases"],
                today_hearings=hearings_overview["today"]["total"],
                today_pending_hearings=hearings_overview["today"]["pending"],
                this_week_hearings=hearings_overview["this_week"]["total"],
                overdue_cases=cases_overview["overdue_cases"],
            ),

            chamber_management=ChamberManagementStats(
                total_users=chamber_stats["total_users"],
                active_users=chamber_stats["active_users"],
                roles_count=chamber_stats["roles_count"],
                users_trend_pct=chamber_stats.get("users_trend_pct", 0),
                active_users_trend_pct=chamber_stats.get("active_users_trend_pct", 0),
            ),

            overdue_cases=overdue_cases,

            todays_hearings=[
                await self._to_hearing_item(r, hearing_status_maps)
                for r in today_rows
            ],

            tomorrows_hearings=[
                await self._to_hearing_item(r, hearing_status_maps)
                for r in tomorrow_rows
            ],
        )

        return mainDashboardOut

    # ===================================================================
    # ADMIN DASHBOARD
    # ===================================================================

    async def get_admin_dashboard(self) -> AdminDashboardOut:
        today = date.today()
        cid = self.chamber_id

        # All stats + trends in ONE repository call
        chamber_stats = await self.dashboard_repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid, today=today
        )
        
        recent_activity = await self.get_recent_activity()

        return AdminDashboardOut(
            stat_cards=AdminStatCards(
                total_users=chamber_stats["total_users"],
                active_users=chamber_stats["active_users"],
                roles_defined=chamber_stats["roles_count"],
                users_trend_pct=chamber_stats.get("users_trend_pct"),
                active_users_trend_pct=chamber_stats.get("active_users_trend_pct"),
            ),
            recent_activity=recent_activity,
        )

    async def get_cases_client_counts(self) -> SummaryCountsOut:
        user: UserOut = self.userDetails

        chamber_id = self.chamber_id
        user_id = user.user_id

        role: Optional[RoleOut] = user.role
        is_admin = bool(role.admin_ind) if role else False

        permissions: List[RolePermissionModuleOut] = user.permissions or []

        has_case_access = any(
            p.module_code == RefmModulesConstants.CASES and p.read_ind
            for p in permissions
        )

        has_client_access = any(
            p.module_code == RefmModulesConstants.CLIENTS and p.read_ind
            for p in permissions
        )

        total_cases = 0
        if has_case_access or is_admin:
            total_cases = await self.dashboard_repo.get_case_count(
                session=self.session,
                chamber_id=chamber_id,
                user_id=user_id,
                is_admin=is_admin,
            )

        total_clients = 0
        if has_client_access or is_admin:
            total_clients = await self.dashboard_repo.get_client_count(
                session=self.session,
                chamber_id=chamber_id,
                user_id=user_id,
                is_admin=is_admin,
            )

        return SummaryCountsOut(
            total_cases=total_cases,
            total_clients=total_clients,
        )

    # ─────────────────────────────────────────────────────────────────────
    # RECENT ACTIVITY
    # ─────────────────────────────────────────────────────────────────────

    async def get_recent_activity(
        self, 
        limit: int = 10
    ) -> List[RecentActivityItem]:
        activity_rows = await self.activity_log_repo.get_recent_activity(session=self.session,
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

        return [
            format_activity(
                log=r,
                actor_name=actor_map.get(r.actor_user_id) if r.actor_user_id else "System",
            )
            for r in activity_rows
        ]
    

    async def get_recent_activity_paged(
        self, 
        page: int,
        limit: int,
    ) -> PagingData[RecentActivityItem]:
        activity_rows, total = await self.activity_log_repo.get_recent_activity_paged(
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