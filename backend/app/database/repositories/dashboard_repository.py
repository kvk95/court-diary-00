"""dashboard_repository.py"""

from datetime import date, timedelta
from typing import Dict, Any

from sqlalchemy import func, select, case, distinct, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.database.models.activity_log import ActivityLog
from app.database.models.case_aors import CaseAors
from app.database.models.cases import Cases
from app.database.models.clients import Clients
from app.database.models.hearings import Hearings
from app.database.models.refm_case_status import RefmCaseStatusConstants
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatusConstants
from app.database.models.refm_invitation_status import RefmInvitationStatusConstants
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

        # =========================
        # CASE METRICS (apply visibility)
        # =========================
        case_stmt = select(
            func.count(
                case((Cases.status_code == RefmCaseStatusConstants.ACTIVE, 1))
            ).label("total_active_cases"),

            func.count(
                case((
                    (Cases.status_code == RefmCaseStatusConstants.ACTIVE) &
                    (Cases.next_hearing_date < today),
                    1
                ))
            ).label("overdue_cases"),
        )

        case_stmt = self.apply_case_visibility(case_stmt)

        case_result = (await session.execute(case_stmt)).one()

        # =========================
        # HEARING METRICS (FIXED 🔥)
        # =========================
        hearing_stmt = (
            select(
                func.count(case((Hearings.hearing_date == today, 1))).label("today_total"),

                func.count(
                    case((
                        (Hearings.hearing_date == today) &
                        (Hearings.status_code.in_([
                            RefmHearingStatusConstants.COMPLETED,
                            RefmHearingStatusConstants.DISPOSED,
                        ])),
                        1
                    ))
                ).label("today_completed"),

                func.count(
                    case((
                        (Hearings.hearing_date == today) &
                        (Hearings.status_code.notin_([
                            RefmHearingStatusConstants.COMPLETED,
                            RefmHearingStatusConstants.DISPOSED,
                        ])),
                        1
                    ))
                ).label("today_pending"),

                func.count(
                    case((
                        Hearings.hearing_date.between(today, week_end),
                        1
                    ))
                ).label("this_week_total"),

                func.count(
                    case((
                        (Hearings.hearing_date < today) &
                        (Hearings.status_code.notin_([
                            RefmHearingStatusConstants.COMPLETED,
                            RefmHearingStatusConstants.DISPOSED,
                        ])),
                        1
                    ))
                ).label("overdue_hearings"),
            )
            .select_from(Hearings)
            .join(Cases, Hearings.case_id == Cases.case_id)  # ✅ IMPORTANT
            .where(Hearings.deleted_ind.is_(False))
        )

        hearing_stmt = self.apply_case_visibility(hearing_stmt)

        hearing_result = (await session.execute(hearing_stmt)).one()

        # =========================
        # CASES WITH HEARING TODAY (FIXED 🔥)
        # =========================
        cases_today_stmt = (
            select(func.count(distinct(Hearings.case_id)))
            .select_from(Hearings)
            .join(Cases, Hearings.case_id == Cases.case_id)
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date == today,
            )
        )

        cases_today_stmt = self.apply_case_visibility(cases_today_stmt)

        cases_today = (await session.execute(cases_today_stmt)).scalar() or 0

        return {
            "cases_overview": {
                "total_active_cases": case_result.total_active_cases or 0,
                "overdue_cases": case_result.overdue_cases or 0,
                "cases_with_hearing_today": cases_today,
            },
            "hearings_overview": {
                "today": {
                    "total": hearing_result.today_total or 0,
                    "completed": hearing_result.today_completed or 0,
                    "pending": hearing_result.today_pending or 0,
                },
                "this_week": {
                    "total": hearing_result.this_week_total or 0,
                },
                "overdue": hearing_result.overdue_hearings or 0,
            },
        }

    # ===================================================================
    # OVERDUE CASES
    # ===================================================================

    async def get_overdue_cases(
        self, session: AsyncSession, chamber_id: str, today: date, limit: int = 10
    ) -> list:

        # =========================
        # SUBQUERY: LAST HEARING
        # =========================
        last_hearing_sq = (
            select(
                Hearings.case_id.label("case_id"),
                func.max(Hearings.hearing_date).label("last_hearing_date"),
            )
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date < today,
            )
            .group_by(Hearings.case_id)
            .subquery()
        )

        last_hearing = aliased(Hearings)

        # =========================
        # SUBQUERY: NEXT HEARING
        # =========================
        next_hearing_sq = (
            select(
                Hearings.case_id.label("case_id"),
                func.min(Hearings.hearing_date).label("next_hearing_date"),
            )
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.hearing_date >= today,
            )
            .group_by(Hearings.case_id)
            .subquery()
        )

        next_hearing = aliased(Hearings)

        # =========================
        # MAIN QUERY
        # =========================
        stmt = (
            select(
                Cases.case_id,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                Cases.status_code,
                RefmCourts.court_name,

                # from cases (fast access)
                Cases.next_hearing_date.label("case_next_hearing_date"),

                # derived
                last_hearing_sq.c.last_hearing_date,
                next_hearing_sq.c.next_hearing_date,

                # purpose (prefer next, fallback last)
                func.coalesce(
                    next_hearing.purpose_code,
                    last_hearing.purpose_code
                ).label("purpose_code"),
            )
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)

            # last hearing join
            .outerjoin(
                last_hearing_sq,
                last_hearing_sq.c.case_id == Cases.case_id
            )
            .outerjoin(
                last_hearing,
                and_(
                    last_hearing.case_id == last_hearing_sq.c.case_id,
                    last_hearing.hearing_date == last_hearing_sq.c.last_hearing_date,
                )
            )

            # next hearing join
            .outerjoin(
                next_hearing_sq,
                next_hearing_sq.c.case_id == Cases.case_id
            )
            .outerjoin(
                next_hearing,
                and_(
                    next_hearing.case_id == next_hearing_sq.c.case_id,
                    next_hearing.hearing_date == next_hearing_sq.c.next_hearing_date,
                )
            )

            # filters
            .where(
                Cases.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
                Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                Cases.next_hearing_date < today,  # overdue
            )

            .order_by(Cases.next_hearing_date.asc())
            .limit(limit)
        )
        stmt = self.apply_case_visibility(stmt)
        rows = await session.execute(stmt)

        return [dict(row._mapping) for row in rows.all()]

    # ===================================================================
    # HEARINGS FOR DATE
    # ===================================================================

    async def get_hearings_for_date(
        self, session: AsyncSession, chamber_id: str, hearing_date: date
    ) -> list:
        stmt = (
            select(
                Hearings.hearing_id,
                Hearings.case_id,
                Hearings.hearing_date,
                Hearings.status_code,
                Hearings.purpose_code,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                RefmCourts.court_name,
            )
            .join(Cases, Hearings.case_id == Cases.case_id)
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .where(
                Hearings.chamber_id == chamber_id,
                Hearings.hearing_date == hearing_date,
                Cases.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),                
                Hearings.deleted_ind.is_(False)
            )
            .order_by(Cases.case_number.asc())
        )
        stmt = self.apply_case_visibility(stmt)

        rows = await session.execute(stmt)
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
                UserInvitations.status_code == RefmInvitationStatusConstants.PENDING,
            )
        ) or 0

        # --- MoM Trend Calculation ---
        month_start = date(today.year, today.month, 1)

        prev_total_users = await session.scalar(
            select(func.count(UserChamberLink.link_id)).where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.status_ind.is_(True),

                # existed before this month
                UserChamberLink.joined_date < month_start,

                # NOT left before this month
                (
                    (UserChamberLink.left_date.is_(None)) |
                    (UserChamberLink.left_date >= month_start)
                ),
            )
        ) or 0

        prev_active_users = await session.scalar(
            select(func.count(UserChamberLink.link_id))
            .join(Users, UserChamberLink.user_id == Users.user_id)
            .where(
                UserChamberLink.chamber_id == chamber_id,
                UserChamberLink.status_ind.is_(True),
                Users.status_ind.is_(True),
                Users.deleted_ind.is_(False),

                UserChamberLink.joined_date < month_start,

                (
                    (UserChamberLink.left_date.is_(None)) |
                    (UserChamberLink.left_date >= month_start)
                ),
            )
        ) or 0

        users_trend = round(((total_users - prev_total_users) / prev_total_users * 100), 1) if prev_total_users > 0 else 0
        active_trend = round( ((active_users - prev_active_users) / prev_active_users * 100), 1 ) if prev_active_users > 0 else 0

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
                UserInvitations.status_code == RefmInvitationStatusConstants.PENDING,
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
    
    from sqlalchemy import select, func, exists, and_

    async def get_case_count(
        self,
        session: AsyncSession,
        chamber_id: str,
        user_id: str,
        is_admin: bool,
    ) -> int:

        stmt = select(func.count(Cases.case_id)).where(
            Cases.chamber_id == chamber_id,
            Cases.deleted_ind.is_(False),
        )

        if not is_admin:
            stmt = stmt.where(
                exists().where(
                    and_(
                        CaseAors.case_id == Cases.case_id,
                        CaseAors.user_id == user_id,
                        CaseAors.chamber_id == chamber_id,
                        CaseAors.withdrawal_date.is_(None),
                    )
                )
            )

        return (await session.scalar(stmt)) or 0
    
    async def get_client_count(self, 
                               session: AsyncSession, 
                               chamber_id: str, 
                               user_id: str, 
                               is_admin: bool) -> int:
        stmt = select(func.count(Clients.client_id)).where(
            Clients.chamber_id == chamber_id,
            Clients.deleted_ind.is_(False),
        )

        if not is_admin:
            stmt = stmt.where(Clients.created_by == user_id)

        return (await session.scalar(stmt)) or 0