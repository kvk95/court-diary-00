# app/services/dashboard_service.py

from datetime import date, datetime, timedelta
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.hearings import Hearings
from app.database.models.refm_modules import RefmModulesConstants
from app.database.repositories.dashboard_repository import DashboardRepository
from app.dtos.dashboard_dto import (
    AdminDashboardOut,
    AdminStatCards,
    ChamberManagementStats,
    DashboardHearingItem,
    MainDashboardOut,
    OverdueCaseItem,
    PendingInvitationItem,
    PracticeOverviewStats,
    RecentActivityItem,
    SummaryCountsOut,
)
from app.dtos.role_permissions_dto import RolePermissionModuleOut
from app.dtos.roles_dto import RoleOut
from app.dtos.users_dto import UserOut
from app.services.base.secured_base_service import BaseSecuredService


def _greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def _full_name(first: Optional[str], last: Optional[str]) -> str:
    return " ".join(p for p in [first, last] if p) or "User"


def _trend_pct(current: int, previous: int) -> Optional[float]:
    """Calculate month-over-month percentage change. Returns None if previous is 0."""
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


class DashboardService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        dashboard_repo: Optional[DashboardRepository] = None,
    ):
        super().__init__(session)
        self.repo = dashboard_repo or DashboardRepository()

    # ===================================================================
    # HELPERS
    # ===================================================================

    async def _get_hearing_status_maps(self):
        """Load both description and color maps once."""
        desc_rows = await self.session.execute(
            select(RefmHearingStatus.code, RefmHearingStatus.description)
        )
        color_rows = await self.session.execute(
            select(RefmHearingStatus.code, RefmHearingStatus.color_code)
        )
        return (
            {r.code: r.description for r in desc_rows},
            {r.code: r.color_code for r in color_rows},
        )

    async def _to_hearing_item(self, r: dict, desc_map: dict, color_map: dict) -> DashboardHearingItem:
        """Convert dict row to DashboardHearingItem DTO."""
        return DashboardHearingItem(
            hearing_id=r["hearing_id"],
            case_id=r["case_id"],
            case_number=r["case_number"],
            court_name=r["court_name"],
            petitioner=r["petitioner"],
            respondent=r["respondent"],
            hearing_date=r["hearing_date"],
            purpose_code=r["purpose_code"],            
            purpose_description=await self.refm_resolver.from_column(
                column_attr=Hearings.purpose_code,
                code=r["purpose_code"],
                value_column=RefmHearingPurpose.description,
                default=None
            ),
            status_code=r["status_code"],
            status_description=desc_map.get(r["status_code"]),
            color=color_map.get(r["status_code"]),
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
        overview = await self.repo.get_practice_overview(
            session=self.session, chamber_id=cid, today=today
        )
        chamber_stats = await self.repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid, today=today
        )
        overdue_rows = await self.repo.get_overdue_cases(
            session=self.session, chamber_id=cid, today=today
        )
        today_rows = await self.repo.get_hearings_for_date(
            session=self.session, chamber_id=cid, hearing_date=today
        )
        tomorrow_rows = await self.repo.get_hearings_for_date(
            session=self.session, chamber_id=cid, hearing_date=tomorrow
        )

        desc_map, color_map = await self._get_hearing_status_maps()

        # =========================
        # EXTRACT NEW STRUCTURE
        # =========================
        cases_overview = overview["cases_overview"]
        hearings_overview = overview["hearings_overview"]

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
                last_hearing_purpose=await self.refm_resolver.from_column(
                    column_attr=Hearings.purpose_code,
                    code=r.get("purpose_code"),
                    value_column=RefmHearingPurpose.description,
                    default=None,
                ),
            )
            for r in overdue_rows
        ]

        # =========================
        # BUILD RESPONSE
        # =========================
        mainDashboardOut: MainDashboardOut = MainDashboardOut(
            greeting=_greeting(hour),
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
                pending_invites=chamber_stats["pending_invites"],
                users_trend_pct=chamber_stats.get("users_trend_pct", 0),
                active_users_trend_pct=chamber_stats.get("active_users_trend_pct", 0),
            ),

            overdue_cases=overdue_cases,

            todays_hearings=[
                await self._to_hearing_item(r, desc_map, color_map)
                for r in today_rows
            ],

            tomorrows_hearings=[
                await self._to_hearing_item(r, desc_map, color_map)
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
        chamber_stats = await self.repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid, today=today
        )

        invitations_rows = await self.repo.get_pending_invitations(
            session=self.session, chamber_id=cid
        )
        activity_rows = await self.repo.get_recent_activity(
            session=self.session, chamber_id=cid
        )

        # Convert pending invitations (dict rows)
        pending_invitations = [
            PendingInvitationItem(
                invitation_id=r["invitation_id"],
                email=r["email"],
                invited_date=r["invited_date"],
                expires_date=r["expires_date"],
                status_code=r["status_code"],
                role_name=r.get("role_name"),
            )
            for r in invitations_rows
        ]

        # Convert recent activity (dict rows)
        recent_activity = [
            RecentActivityItem(
                activity_id=r["activity_id"],
                action=r["action"],
                target=r["target"],
                actor_name=_full_name(r.get("first_name"), r.get("last_name")),
                created_date=r["created_date"],
            )
            for r in activity_rows
        ]

        return AdminDashboardOut(
            stat_cards=AdminStatCards(
                total_users=chamber_stats["total_users"],
                active_users=chamber_stats["active_users"],
                roles_defined=chamber_stats["roles_count"],
                pending_invites=chamber_stats["pending_invites"],
                users_trend_pct=chamber_stats.get("users_trend_pct"),
                active_users_trend_pct=chamber_stats.get("active_users_trend_pct"),
            ),
            pending_invitations=pending_invitations,
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
            total_cases = await self.repo.get_case_count(
                session=self.session,
                chamber_id=chamber_id,
                user_id=user_id,
                is_admin=is_admin,
            )

        total_clients = 0
        if has_client_access or is_admin:
            total_clients = await self.repo.get_client_count(
                session=self.session,
                chamber_id=chamber_id,
                user_id=user_id,
                is_admin=is_admin,
            )

        return SummaryCountsOut(
            total_cases=total_cases,
            total_clients=total_clients,
        )