"""dashboard_service.py — Business logic for Main Dashboard and Admin Dashboard"""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

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
    """Month-over-month % change. Returns None when previous is 0."""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


class DashboardService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        dashboard_repo: Optional[DashboardRepository] = None,
    ):
        super().__init__(session)
        self.repo = dashboard_repo or DashboardRepository()

    # ─────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _get_status_color_map(self) -> dict:
        """Load hearing status colors once per request."""
        from sqlalchemy import select
        rows = await self.session.execute(
            select(RefmHearingStatus.code, RefmHearingStatus.color_code)
        )
        return {r.code: r.color_code for r in rows}

    async def _get_status_desc_map(self) -> dict:
        from sqlalchemy import select
        rows = await self.session.execute(
            select(RefmHearingStatus.code, RefmHearingStatus.description)
        )
        return {r.code: r.description for r in rows}

    def _to_hearing_item(self, r, desc_map: dict, color_map: dict) -> DashboardHearingItem:
        return DashboardHearingItem(
            hearing_id=r.hearing_id,
            case_id=r.case_id,
            case_number=r.case_number,
            court_name=r.court_name,
            petitioner=r.petitioner,
            respondent=r.respondent,
            hearing_date=r.hearing_date,
            purpose=r.purpose,
            status_code=r.status_code,
            status_description=desc_map.get(r.status_code) if r.status_code else None,
            color=color_map.get(r.status_code) if r.status_code else None,
        )

    # ─────────────────────────────────────────────────────────────────────
    # MAIN DASHBOARD
    # ─────────────────────────────────────────────────────────────────────

    async def get_main_dashboard(self, user_first_name: str) -> MainDashboardOut:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        cid = self.chamber_id
        hour = datetime.now().hour

        # All dashboard queries via repo
        overview = await self.repo.get_practice_overview(
            session=self.session, chamber_id=cid, today=today
        )
        chamber_stats = await self.repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid
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

        desc_map = await self._get_status_desc_map()
        color_map = await self._get_status_color_map()

        overdue_cases = [
            OverdueCaseItem(
                case_id=r["case_id"],
                case_number=r["case_number"],
                court_name=r["court_name"],
                petitioner=r["petitioner"],
                respondent=r["respondent"],
                next_hearing_date=r["next_hearing_date"],
                days_overdue=(today - r["next_hearing_date"]).days if r["next_hearing_date"] else 0,
                last_hearing_purpose=r["last_hearing_purpose"],
            )
            for r in overdue_rows
        ]

        return MainDashboardOut(
            greeting=_greeting(hour),
            user_first_name=user_first_name,
            today=today,
            active_cases_count=overview["active_cases"],
            today_hearings_count=overview["today_hearings"],
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
            ),
            overdue_cases=overdue_cases,
            todays_hearings=[self._to_hearing_item(r, desc_map, color_map) for r in today_rows],
            tomorrows_hearings=[self._to_hearing_item(r, desc_map, color_map) for r in tomorrow_rows],
        )

    # ─────────────────────────────────────────────────────────────────────
    # ADMIN DASHBOARD
    # ─────────────────────────────────────────────────────────────────────

    async def get_admin_dashboard(self) -> AdminDashboardOut:
        today = date.today()
        month_start = date(today.year, today.month, 1)
        cid = self.chamber_id

        # Stat cards (reuse chamber management stats)
        chamber_stats = await self.repo.get_chamber_management_stats(
            session=self.session, chamber_id=cid
        )

        # MoM trends for users
        prev_total = await self.repo.get_users_last_month_count(
            session=self.session, chamber_id=cid, month_start=month_start
        )
        users_trend = _trend_pct(chamber_stats["total_users"], prev_total)
        # active_users trend approximated from same base
        active_trend = _trend_pct(chamber_stats["active_users"], max(prev_total - 1, 0))

        invitations_rows = await self.repo.get_pending_invitations(
            session=self.session, chamber_id=cid
        )
        activity_rows = await self.repo.get_recent_activity(
            session=self.session, chamber_id=cid
        )

        pending_invitations = [
            PendingInvitationItem(
                invitation_id=r.invitation_id,
                email=r.email,
                role_name=r.role_name,
                invited_date=r.invited_date,
                expires_date=r.expires_date,
                status_code=r.status_code,
            )
            for r in invitations_rows
        ]

        recent_activity = [
            RecentActivityItem(
                activity_id=r.id,
                action=r.action,
                target=r.target,
                actor_name=_full_name(r.first_name, r.last_name),
                created_date=r.created_date,
            )
            for r in activity_rows
        ]

        return AdminDashboardOut(
            stat_cards=AdminStatCards(
                total_users=chamber_stats["total_users"],
                active_users=chamber_stats["active_users"],
                roles_defined=chamber_stats["roles_count"],
                pending_invites=chamber_stats["pending_invites"],
                users_trend_pct=users_trend,
                active_users_trend_pct=active_trend,
            ),
            pending_invitations=pending_invitations,
            recent_activity=recent_activity,
        )
