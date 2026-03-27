"""dashboard_repository.py"""

from datetime import date, timedelta
from typing import Dict, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.activity_log import ActivityLog
from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_courts import RefmCourts
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_invitations import UserInvitations
from app.database.models.user_roles import UserRoles
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class DashboardRepository(BaseRepository[Cases]):
    """
    All dashboard-related aggregate queries.
    """

    def __init__(self):
        super().__init__(Cases)

    # ===================================================================
    # PRACTICE OVERVIEW
    # ===================================================================

    async def get_practice_overview(
        self, session: AsyncSession, chamber_id: str, today: date
    ) -> Dict[str, Any]:
        week_end = today + timedelta(days=6)

        active_cases = await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.status_code == "AC",
            )
        ) or 0

        today_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date == today,
            )
        ) or 0

        today_overdue_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id))
            .join(Cases, Hearings.case_id == Cases.case_id)
            .where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),
                Hearings.hearing_date == today,
                Hearings.status_code.notin_(["CMP", "DIS"]),
            )
        ) or 0

        this_week_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date.between(today, week_end),
            )
        ) or 0

        overdue_cases = await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.status_code == "AC",
                Cases.next_hearing_date < today,
            )
        ) or 0

        return {
            "active_cases": active_cases,
            "today_hearings": today_hearings,
            "today_overdue_hearings": today_overdue_hearings,
            "this_week_hearings": this_week_hearings,
            "overdue_cases": overdue_cases,
        }

    # ===================================================================
    # OVERDUE CASES
    # ===================================================================

    async def get_overdue_cases(
        self, session: AsyncSession, chamber_id: str, today: date, limit: int = 10
    ) -> list:
        rows = await session.execute(
            select(
                Cases.case_id,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                Cases.next_hearing_date,
                Cases.status_code,
                RefmCourts.court_name,
            )
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .where(
                Cases.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.status_code == "AC",
                Cases.next_hearing_date < today,
            )
            .order_by(Cases.next_hearing_date.asc())
            .limit(limit)
        )

        case_rows = [dict(row._mapping) for row in rows.all()]
        if not case_rows:
            return []

        case_ids = [r["case_id"] for r in case_rows]

        purpose_rows = await session.execute(
            select(
                Hearings.case_id,
                Hearings.purpose,
            )
            .where(
                Hearings.case_id.in_(case_ids),
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date == (
                    select(func.max(Hearings.hearing_date))
                    .where(Hearings.case_id == Hearings.case_id, Hearings.deleted_ind.is_(False))
                    .correlate(Hearings)
                    .scalar_subquery()
                ),
            )
        )
        purpose_map = {r.case_id: r.purpose for r in purpose_rows.all()}

        for r in case_rows:
            r["last_hearing_purpose"] = purpose_map.get(r["case_id"])

        return case_rows

    # ===================================================================
    # HEARINGS FOR DATE
    # ===================================================================

    async def get_hearings_for_date(
        self, session: AsyncSession, chamber_id: str, hearing_date: date
    ) -> list:
        rows = await session.execute(
            select(
                Hearings.hearing_id,
                Hearings.case_id,
                Hearings.hearing_date,
                Hearings.status_code,
                Hearings.purpose,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                RefmCourts.court_name,
            )
            .join(Cases, Hearings.case_id == Cases.case_id)
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),
                Hearings.hearing_date == hearing_date,
            )
            .order_by(Cases.case_number.asc())
        )
        return [dict(row._mapping) for row in rows.all()]

    # ===================================================================
    # CHAMBER MANAGEMENT STATS + TREND (Moved here)
    # ===================================================================

    async def get_chamber_management_stats(
        self, session: AsyncSession, chamber_id: str, today: date
    ) -> Dict[str, Any]:
        """Returns stats + MoM trends."""

        total_users = await session.scalar(
            select(func.count(UserChamberLink.link_id)).where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
            )
        ) or 0

        active_users = await session.scalar(
            select(func.count(UserChamberLink.link_id))
            .join(Users, UserChamberLink.user_id == Users.user_id)
            .where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
                Users.status_ind.is_(True),
                Users.deleted_ind.is_(False),
            )
        ) or 0

        roles_count = await session.scalar(
            select(func.count(func.distinct(UserRoles.role_id)))
            .join(UserChamberLink, UserChamberLink.link_id == UserRoles.link_id)
            .where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
                UserRoles.end_date.is_(None),
            )
        ) or 0

        pending_invites = await session.scalar(
            select(func.count(UserInvitations.invitation_id)).where(
                UserInvitations.chamber_id == chamber_id,
                UserInvitations.status_code == "PN",
            )
        ) or 0

        # --- MoM Trend Calculation ---
        month_start = date(today.year, today.month, 1)
        last_month_start = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)

        prev_total_users = await session.scalar(
            select(func.count(UserChamberLink.link_id)).where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.left_date.is_(None),
                UserChamberLink.status_ind.is_(True),
                UserChamberLink.joined_date < month_start,
            )
        ) or 0

        users_trend = round(((total_users - prev_total_users) / prev_total_users * 100), 1) if prev_total_users > 0 else 0
        active_trend = round(((active_users - prev_total_users) / prev_total_users * 100), 1) if prev_total_users > 0 else 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "roles_count": roles_count,
            "pending_invites": pending_invites,
            "users_trend_pct": users_trend,
            "active_users_trend_pct": active_trend,
        }

    # ===================================================================
    # PENDING INVITATIONS & RECENT ACTIVITY
    # ===================================================================

    async def get_pending_invitations(
        self, session: AsyncSession, chamber_id: str, limit: int = 10
    ) -> list:
        rows = await session.execute(
            select(
                UserInvitations.invitation_id,
                UserInvitations.email,
                UserInvitations.invited_date,
                UserInvitations.expires_date,
                UserInvitations.status_code,
                ChamberRoles.role_name,
            )
            .outerjoin(ChamberRoles, UserInvitations.role_id == ChamberRoles.role_id)
            .where(
                UserInvitations.chamber_id == chamber_id,
                UserInvitations.status_code == "PN",
            )
            .order_by(UserInvitations.invited_date.desc())
            .limit(limit)
        )
        return [dict(row._mapping) for row in rows.all()]

    async def get_recent_activity(
        self, session: AsyncSession, chamber_id: str, limit: int = 10
    ) -> list:
        rows = await session.execute(
            select(
                ActivityLog.id.label("activity_id"),
                ActivityLog.action,
                ActivityLog.target,
                ActivityLog.created_date,
                Users.first_name,
                Users.last_name,
            )
            .outerjoin(Users, ActivityLog.user_id == Users.user_id)
            .where(ActivityLog.chamber_id == chamber_id)
            .order_by(ActivityLog.created_date.desc())
            .limit(limit)
        )
        return [dict(row._mapping) for row in rows.all()]