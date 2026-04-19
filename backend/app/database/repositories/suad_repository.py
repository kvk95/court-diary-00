# app/database/repositories/suad_repository.py

from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy import func, or_, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber import Chamber
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.login_audit import LoginAudit
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.models.cases import Cases
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.refm_case_status import RefmCaseStatusConstants
from app.database.models.refm_plan_types import RefmPlanTypes, RefmPlanTypesConstants, RefmPlanTypesEnum

from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class SuadRepository(BaseRepository[Chamber]):
    """
    Super Admin (SUAD) Repository
    - No chamber restriction
    - Platform-wide queries
    """

    def __init__(self):
        super().__init__(Chamber)

    # ---------------------------------------------------------------------
    # DASHBOARD STATS
    # ---------------------------------------------------------------------
    async def get_dashboard_stats(
        self, session: AsyncSession, today: date
    ) -> Dict[str, Any]:

        # --- Total Chambers ---
        total_chambers = await self.execute_scalar(
            session=session,
            stmt=select(func.count(Chamber.chamber_id)).where(
                Chamber.deleted_ind.is_(False)
            ),
            include_chamber_id=False,
        )

        # --- Total Users ---
        total_users = await self.execute_scalar(
            session=session,
            stmt=select(func.count(Users.user_id)).where(
                Users.deleted_ind.is_(False)
            ),
            include_chamber_id=False,
        )

        # --- Active Cases (FIXED LOGIC) ---
        active_cases = await self.execute_scalar(
            session=session,
            stmt=select(func.count(Cases.case_id)).where(
                Cases.deleted_ind.is_(False),
                Cases.status_code.notin_(
                    [
                        RefmCaseStatusConstants.DISPOSED,
                        RefmCaseStatusConstants.CLOSED,
                    ]
                ),
            ),
            include_chamber_id=False,
        )

        # --- Active Subscriptions ---
        active_subscriptions = await self.execute_scalar(
            session=session,
            stmt=select(func.count(Chamber.chamber_id)).where(
                Chamber.deleted_ind.is_(False),
                Chamber.status_ind.is_(True),
                (
                    (Chamber.subscription_end >= today)
                    | (Chamber.subscription_end.is_(None))
                ),
            ),
            include_chamber_id=False,
        )

        # --- Monthly Revenue (REAL) ---
        monthly_revenue = await self.execute_scalar(
            session=session,
            stmt=(
                select(func.coalesce(func.sum(RefmPlanTypes.price_monthly_amt), 0))
                .select_from(Chamber)
                .join(
                    RefmPlanTypes,
                    Chamber.plan_code == RefmPlanTypes.code,
                )
                .where(
                    Chamber.deleted_ind.is_(False),
                    Chamber.status_ind.is_(True),
                )
            ),
            include_chamber_id=False,
        )

        # --- System Health (basic placeholder, can upgrade later) ---
        system_health = 99.9 if (total_chambers or 0) > 0 else 95.0

        return {
            "total_chambers": total_chambers or 0,
            "total_users": total_users or 0,
            "active_cases": active_cases or 0,
            "active_subscriptions": active_subscriptions or 0,
            "monthly_revenue": float(monthly_revenue or 0),
            "system_health": system_health,
        }

    # ---------------------------------------------------------------------
    # TOP CHAMBERS (FIXED DISTINCT COUNTS)
    # ---------------------------------------------------------------------

    async def get_top_chambers_by_cases(
        self,
        session: AsyncSession,
        limit: int,
        search: str | None = None,
    ) -> List[Dict]:

        stmt = (
            select(
                Chamber.chamber_id,
                Chamber.chamber_name,
                Chamber.plan_code,
                func.count(func.distinct(Cases.case_id)).label("cases_count"),
                func.count(func.distinct(UserChamberLink.link_id)).label("users_count"),
            )
            .outerjoin(Cases, Cases.chamber_id == Chamber.chamber_id)
            .outerjoin(UserChamberLink, UserChamberLink.chamber_id == Chamber.chamber_id)
            .where(Chamber.deleted_ind.is_(False))
        )

        # 🔍 APPLY SEARCH FILTER
        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                Chamber.chamber_name.ilike(kw)
            )

        stmt = (
            stmt.group_by(
                Chamber.chamber_id,
                Chamber.chamber_name,
                Chamber.plan_code,
            )
            .order_by(func.count(func.distinct(Cases.case_id)).desc())
            .limit(limit)
        )

        result = await self.execute(
            session=session,
            stmt=stmt,
            include_chamber_id=False,
        )

        rows = result.all()

        # Plan mapping
        plan_map = {plan.value: plan.name for plan in RefmPlanTypesEnum}

        return [
            {
                "rank": i + 1,
                "chamber_id": str(row.chamber_id),
                "chamber_name": row.chamber_name,
                "users_count": row.users_count or 0,
                "cases_count": row.cases_count or 0,
                "plan": plan_map.get(row.plan_code, RefmPlanTypesConstants.FREE),
            }
            for i, row in enumerate(rows)
        ]
    
    async def get_stats(self, session) -> Dict[str, int]:

        stmt = select(
            func.count(Chamber.chamber_id).label("total"),

            func.sum(case((Chamber.status_ind == True, 1), else_=0)).label("active"),

            func.sum(case((Chamber.plan_code == "PTFR", 1), else_=0)).label("trial"),

            func.sum(case((Chamber.status_ind == False, 1), else_=0)).label("suspended"),
        ).where(Chamber.deleted_ind.is_(False))

        row = (await session.execute(stmt)).one()

        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "trial": row.trial or 0,
            "suspended": row.suspended or 0,
        }


    async def list_chambers(
        self,
        session,
        page: int,
        limit: int,
        search: Optional[str],
        status: Optional[str],
    ) -> Tuple[List[Dict[str, Any]], int]:

        stmt = (
            select(
                Chamber.chamber_id,
                Chamber.chamber_name,
                Chamber.created_date.label("joined_date"),
                Chamber.plan_code,
                Chamber.status_ind,

                func.count(func.distinct(UserChamberLink.link_id)).label("users_count"),
                func.count(func.distinct(Cases.case_id)).label("cases_count"),
            )
            .outerjoin(UserChamberLink, UserChamberLink.chamber_id == Chamber.chamber_id)
            .outerjoin(Cases, Cases.chamber_id == Chamber.chamber_id)
            .where(Chamber.deleted_ind.is_(False))
            .group_by(Chamber.chamber_id)
        )

        # 🔍 search
        if search:
            kw = f"%{search}%"
            stmt = stmt.where(Chamber.chamber_name.ilike(kw))

        # 🎯 status filter
        if status == "ACTIVE":
            stmt = stmt.where(Chamber.status_ind.is_(True))
        elif status == "SUSPENDED":
            stmt = stmt.where(Chamber.status_ind.is_(False))

        # count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar()

        # pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await session.execute(stmt)).all()

        result = []
        for r in rows:
            result.append({
                "chamber_id": r.chamber_id,
                "chamber_name": r.chamber_name,
                "owner_name": "TODO",  # we'll improve next

                "users_count": r.users_count or 0,
                "cases_count": r.cases_count or 0,
                "clients_count": 0,  # TODO later

                "plan": "Pro" if r.plan_code == "PTPR" else "Free",
                "status": "Active" if r.status_ind else "Suspended",
                "joined_date": r.joined_date,
            })

        return result, total
    
    async def get_user_stats(self, session) -> Dict[str, int]:

        now = datetime.today()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stmt = select(
            func.count(Users.user_id).label("total"),
            func.sum(case((Users.status_ind == True, 1), else_=0)).label("active"),
            func.sum(case((Users.created_date >= month_start, 1), else_=0)).label("new"),
        ).where(Users.deleted_ind.is_(False))

        row = (await session.execute(stmt)).one()

        return {
            "total": row.total or 0,
            "active": row.active or 0,
            "new_this_month": row.new or 0,
        }


    async def list_users(
        self,
        session,
        page: int,
        limit: int,
        search: str | None,
        status: str | None,
    ) -> Tuple[List[Dict[str, Any]], int]:

        # 🔥 last login subquery
        last_login_subq = (
            select(
                LoginAudit.actor_user_id.label("user_id"),
                func.max(LoginAudit.login_time).label("last_login"),
            )
            .group_by(LoginAudit.actor_user_id)
            .subquery()
        )

        stmt = (
            select(
                Users.user_id,
                Users.first_name,
                Users.last_name,
                Users.email,
                Users.status_ind,

                Chamber.chamber_name,
                ChamberRoles.role_name,

                last_login_subq.c.last_login,
            )
            .join(UserChamberLink, Users.user_id == UserChamberLink.user_id)
            .outerjoin(UserRoles, UserChamberLink.link_id == UserRoles.link_id)
            .outerjoin(ChamberRoles, UserRoles.role_id == ChamberRoles.role_id)
            .outerjoin(Chamber, UserChamberLink.chamber_id == Chamber.chamber_id)
            .outerjoin(last_login_subq, Users.user_id == last_login_subq.c.user_id)
            .where(Users.deleted_ind.is_(False))
        )

        # 🔍 search
        if search:
            kw = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Users.first_name.ilike(kw),
                    Users.last_name.ilike(kw),
                    Users.email.ilike(kw),
                    Chamber.chamber_name.ilike(kw),
                )
            )

        # 🎯 status
        if status == "ACTIVE":
            stmt = stmt.where(Users.status_ind.is_(True))
        elif status == "INACTIVE":
            stmt = stmt.where(Users.status_ind.is_(False))

        # count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar()

        stmt = stmt.offset((page - 1) * limit).limit(limit)

        rows = (await session.execute(stmt)).all()

        result = []
        for r in rows:
            result.append({
                "user_id": r.user_id,
                "full_name": f"{r.first_name or ''} {r.last_name or ''}".strip(),
                "email": r.email,
                "chamber_name": r.chamber_name,
                "role_name": r.role_name,
                "status": "Active" if r.status_ind else "Inactive",
                "last_login": r.last_login,
            })

        return result, total