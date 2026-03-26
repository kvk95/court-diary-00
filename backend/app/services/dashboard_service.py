# app/services/dashboard_service.py

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.refm_hearing_status import RefmHearingStatus
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
)
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

    def _to_hearing_item(self, r: dict, desc_map: dict, color_map: dict) -> DashboardHearingItem:
        """Convert dict row to DashboardHearingItem DTO."""
        return DashboardHearingItem(
            hearing_id=r["hearing_id"],
            case_id=r["case_id"],
            case_number=r["case_number"],
            court_name=r["court_name"],
            petitioner=r["petitioner"],
            respondent=r["respondent"],
            hearing_date=r["hearing_date"],
            purpose=r["purpose"],
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

        # Convert overdue cases (dict rows)
        overdue_cases = [
            OverdueCaseItem(
                case_id=r["case_id"],
                case_number=r["case_number"],
                court_name=r["court_name"],
                petitioner=r["petitioner"],
                respondent=r["respondent"],
                next_hearing_date=r["next_hearing_date"],
                days_overdue=(today - r["next_hearing_date"]).days if r.get("next_hearing_date") else 0,
                last_hearing_purpose=r.get("last_hearing_purpose"),
            )
            for r in overdue_rows
        ]

        return MainDashboardOut(
            greeting=_greeting(hour),
            user_first_name=user_first_name,
            active_cases_count=overview["active_cases"],
            today_hearings_count=overview["today_hearings"],
            today=today,
            practice_overview=PracticeOverviewStats(
                active_cases=overview["active_cases"],
                today_hearings=overview["today_hearings"],
                today_overdue_hearings=overview["today_overdue_hearings"],
                this_week_hearings=overview["this_week_hearings"],
                overdue_cases=overview["overdue_cases"],
            ),
            chamber_management=ChamberManagementStats(
                total_users=chamber_stats["total_users"],
                active_users=chamber_stats["active_users"],
                roles_count=chamber_stats["roles_count"],
                pending_invites=chamber_stats["pending_invites"],
                users_trend_pct=chamber_stats.get("users_trend_pct",0),
                active_users_trend_pct=chamber_stats.get("active_users_trend_pct",0),
            ),
            overdue_cases=overdue_cases,
            todays_hearings=[self._to_hearing_item(r, desc_map, color_map) for r in today_rows],
            tomorrows_hearings=[self._to_hearing_item(r, desc_map, color_map) for r in tomorrow_rows],
        )

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