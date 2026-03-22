"""dashboard_repository.py — All DB queries for Main Dashboard and Admin Dashboard"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.activity_log import ActivityLog
from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_courts import RefmCourts
from app.database.models.security_roles import SecurityRoles
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_invitations import UserInvitations
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class DashboardRepository(BaseRepository[Cases]):
    """
    Read-only aggregate queries for both dashboard screens.
    Follows UsersRepository pattern: all queries here, service does DTO mapping only.
    """

    def __init__(self):
        super().__init__(Cases)

    # ─────────────────────────────────────────────────────────────────────
    # PRACTICE OVERVIEW — 4 stat cards (top section, main dashboard)
    # ─────────────────────────────────────────────────────────────────────

    async def get_practice_overview(
        self,
        session: AsyncSession,
        chamber_id: int,
        today: date,
    ) -> dict:
        """
        Returns all 4 stat card values in minimal queries:
          active_cases, today_hearings, today_overdue_hearings,
          this_week_hearings, overdue_cases
        """
        week_end = today + timedelta(days=6)

        active_cases = await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.status_code == "AC",
            )
        ) or 0

        today_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.is_deleted.is_(False),
                Hearings.hearing_date == today,
            )
        ) or 0

        today_overdue_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.is_deleted.is_(False),
                Hearings.hearing_date == today,
                Hearings.status_code.notin_(["CMP", "DIS"]),
                Cases.is_deleted.is_(False),
            )
        ) or 0

        this_week_hearings = await session.scalar(
            select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.is_deleted.is_(False),
                Hearings.hearing_date >= today,
                Hearings.hearing_date <= week_end,
            )
        ) or 0

        overdue_cases = await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
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

    # ─────────────────────────────────────────────────────────────────────
    # OVERDUE CASES — list with hearing info (Overdue Updates section)
    # ─────────────────────────────────────────────────────────────────────

    async def get_overdue_cases(
        self,
        session: AsyncSession,
        chamber_id: int,
        today: date,
        limit: int = 10,
    ) -> list:
        """
        Active cases where next_hearing_date < today.
        Returns rows with: case_id, case_number, court_name,
          petitioner, respondent, next_hearing_date, last_hearing_purpose
        """
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
                Cases.is_deleted.is_(False),
                Cases.status_code == "AC",
                Cases.next_hearing_date < today,
            )
            .order_by(Cases.next_hearing_date.asc())
            .limit(limit)
        )
        case_rows = list(rows.all())

        if not case_rows:
            return []

        # Get last hearing purpose for each overdue case in one query
        case_ids = [r.case_id for r in case_rows]
        purpose_rows = await session.execute(
            select(
                Hearings.case_id,
                Hearings.purpose,
            )
            .where(
                Hearings.case_id.in_(case_ids),
                Hearings.is_deleted.is_(False),
                Hearings.hearing_date == (
                    select(func.max(Hearings.hearing_date))
                    .where(
                        Hearings.case_id == Hearings.case_id,
                        Hearings.is_deleted.is_(False),
                    )
                    .correlate(Hearings)
                    .scalar_subquery()
                ),
            )
        )
        purpose_map = {r.case_id: r.purpose for r in purpose_rows.all()}

        return [
            {
                "case_id": r.case_id,
                "case_number": r.case_number,
                "petitioner": r.petitioner,
                "respondent": r.respondent,
                "next_hearing_date": r.next_hearing_date,
                "status_code": r.status_code,
                "court_name": r.court_name,
                "last_hearing_purpose": purpose_map.get(r.case_id),
            }
            for r in case_rows
        ]

    # ─────────────────────────────────────────────────────────────────────
    # TODAY'S HEARINGS — full list
    # ─────────────────────────────────────────────────────────────────────

    async def get_hearings_for_date(
        self,
        session: AsyncSession,
        chamber_id: int,
        hearing_date: date,
    ) -> list:
        """
        Returns all hearings on a specific date with case + court info.
        Used for Today's Hearings and Tomorrow's Hearings sections.
        """
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
                Hearings.is_deleted.is_(False),
                Cases.is_deleted.is_(False),
                Hearings.hearing_date == hearing_date,
            )
            .order_by(Cases.case_number.asc())
        )
        return list(rows.all())

    # ─────────────────────────────────────────────────────────────────────
    # CHAMBER MANAGEMENT — 3 stat cards (middle section, main dashboard)
    # ─────────────────────────────────────────────────────────────────────

    async def get_chamber_management_stats(
        self,
        session: AsyncSession,
        chamber_id: int,
    ) -> dict:
        """
        total_users, active_users, roles_count, pending_invites
        All in one method to keep queries grouped.
        """
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
                Users.is_deleted.is_(False),
            )
        ) or 0

        roles_count = await session.scalar(
            select(func.count(SecurityRoles.role_id)).where(
                SecurityRoles.chamber_id == chamber_id,
                SecurityRoles.status_ind.is_(True),
            )
        ) or 0

        pending_invites = await session.scalar(
            select(func.count(UserInvitations.invitation_id)).where(
                UserInvitations.chamber_id == chamber_id,
                UserInvitations.status_code == "PN",
            )
        ) or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "roles_count": roles_count,
            "pending_invites": pending_invites,
        }

    # ─────────────────────────────────────────────────────────────────────
    # PENDING INVITATIONS — list for Admin Dashboard widget
    # ─────────────────────────────────────────────────────────────────────

    async def get_pending_invitations(
        self,
        session: AsyncSession,
        chamber_id: int,
        limit: int = 10,
    ) -> list:
        """
        Returns pending invitations with invited_date, email, role_name.
        """
        rows = await session.execute(
            select(
                UserInvitations.invitation_id,
                UserInvitations.email,
                UserInvitations.invited_date,
                UserInvitations.status_code,
                UserInvitations.expires_date,
                SecurityRoles.role_name,
            )
            .outerjoin(SecurityRoles, UserInvitations.role_id == SecurityRoles.role_id)
            .where(
                UserInvitations.chamber_id == chamber_id,
                UserInvitations.status_code == "PN",
            )
            .order_by(UserInvitations.invited_date.desc())
            .limit(limit)
        )
        return list(rows.all())

    # ─────────────────────────────────────────────────────────────────────
    # RECENT ACTIVITY — for Admin Dashboard activity feed
    # ─────────────────────────────────────────────────────────────────────

    async def get_recent_activity(
        self,
        session: AsyncSession,
        chamber_id: int,
        limit: int = 10,
    ) -> list:
        """
        Recent activity log entries with actor name.
        """
        rows = await session.execute(
            select(
                ActivityLog.id,
                ActivityLog.action,
                ActivityLog.target,
                ActivityLog.created_date,
                ActivityLog.user_id,
                Users.first_name,
                Users.last_name,
            )
            .outerjoin(Users, ActivityLog.user_id == Users.user_id)
            .where(ActivityLog.chamber_id == chamber_id)
            .order_by(ActivityLog.created_date.desc())
            .limit(limit)
        )
        return list(rows.all())

    # ─────────────────────────────────────────────────────────────────────
    # MoM DELTA — % change vs last month for stat card trend arrows
    # ─────────────────────────────────────────────────────────────────────

    async def get_users_last_month_count(
        self,
        session: AsyncSession,
        chamber_id: int,
        month_start: date,
    ) -> int:
        """Count of users who joined before start of current month (for % trend)."""
        return await session.scalar(
            select(func.count(UserChamberLink.link_id)).where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.status_ind.is_(True),
                UserChamberLink.left_date.is_(None),
                UserChamberLink.joined_date < month_start,
            )
        ) or 0
