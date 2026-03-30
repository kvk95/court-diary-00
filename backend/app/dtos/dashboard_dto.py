"""dashboard_dto.py — DTOs for Main Dashboard and Admin Dashboard"""

from datetime import date, datetime
from typing import List, Optional

from app.dtos.base.base_data import BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

class PracticeOverviewStats(BaseRecordData):
    """4 stat cards at the top of the main dashboard."""
    active_cases: int = 0
    today_hearings: int = 0
    today_overdue_hearings: int = 0   # shown as "3 overdue" sub-label
    this_week_hearings: int = 0
    overdue_cases: int = 0


class ChamberManagementStats(BaseRecordData):
    """3 stat cards in Chamber Management section."""
    total_users: int = 0
    active_users: int = 0
    roles_count: int = 0
    pending_invites: int = 0
    users_trend_pct: int = 0
    active_users_trend_pct: int = 0


class OverdueCaseItem(BaseRecordData):
    """One row in the Overdue Updates accordion."""
    case_id: str
    case_number: str
    court_name: Optional[str] = None
    petitioner: str
    respondent: str
    next_hearing_date: Optional[date] = None
    days_overdue: int = 0
    last_hearing_purpose: Optional[str] = None


class DashboardHearingItem(BaseRecordData):
    """One row in Today's / Tomorrow's Hearings sections."""
    hearing_id: str
    case_id: str
    case_number: str
    court_name: Optional[str] = None
    petitioner: str
    respondent: str
    hearing_date: date
    purpose_code: Optional[str] = None
    purpose_description: Optional[str] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    color: Optional[str] = None


class MainDashboardOut(BaseRecordData):
    """Complete payload for the main dashboard — one call covers all sections."""
    # Greeting context
    greeting: str                              # "Good morning" / "Good afternoon" / "Good evening"
    user_first_name: str
    today: date
    active_cases_count: int = 0
    today_hearings_count: int = 0

    # Sections
    practice_overview: PracticeOverviewStats
    chamber_management: ChamberManagementStats
    overdue_cases: List[OverdueCaseItem] = []
    todays_hearings: List[DashboardHearingItem] = []
    tomorrows_hearings: List[DashboardHearingItem] = []


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

class AdminStatCards(BaseRecordData):
    """4 stat cards on the Admin Dashboard."""
    total_users: int = 0
    active_users: int = 0
    roles_defined: int = 0
    pending_invites: int = 0
    # Trend indicators (month-over-month)
    users_trend_pct: Optional[float] = None    # e.g. 12.0 → shown as "+12%"
    active_users_trend_pct: Optional[float] = None


class PendingInvitationItem(BaseRecordData):
    """One row in the Pending Invitations widget."""
    invitation_id: str
    email: str
    role_name: Optional[str] = None
    invited_date: Optional[datetime] = None
    expires_date: Optional[date] = None
    status_code: str = "PN"


class RecentActivityItem(BaseRecordData):
    """One row in the Recent Activity feed."""
    activity_id: str
    action: str
    target: Optional[str] = None
    actor_name: Optional[str] = None
    created_date: Optional[datetime] = None


class AdminDashboardOut(BaseRecordData):
    """Complete payload for the Admin Dashboard — one call covers all sections."""
    stat_cards: AdminStatCards
    pending_invitations: List[PendingInvitationItem] = []
    recent_activity: List[RecentActivityItem] = []
