"""cases_repository.py — All DB operations for Cases"""

from datetime import date
from typing import List, Optional

from sqlalchemy import and_, func, select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_aors import CaseAors
from app.database.models.case_clients import CaseClients
from app.database.models.cases import Cases
from app.database.models.chamber import Chamber
from app.database.models.courts import Courts
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.hearings import Hearings
from app.database.models.refm_plan_types import RefmPlanTypes
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class CasesRepository(BaseRepository[Cases]):
    def __init__(self):
        super().__init__(Cases)

    async def get_case_summary_stats(self, session: AsyncSession, today: date) -> dict:
        row = await self.execute(
            session=session,
            stmt=select(
                func.count(Cases.case_id).label("total"),
                func.count(
                    case((Cases.status_code == RefmCaseStatusConstants.ACTIVE, Cases.case_id))
                ).label("active"),
                func.count(
                    case((Cases.status_code == RefmCaseStatusConstants.ADJOURNED, Cases.case_id))
                ).label("adjourned"),
                func.count(
                    case(
                        (
                            (Cases.status_code == RefmCaseStatusConstants.ACTIVE)
                            & (Cases.next_hearing_date < today),
                            Cases.case_id,
                        )
                    )
                ).label("overdue"),
            ),
        )

        r = row.one()
        return dict(r._mapping)
    
    async def get_case_summary(
        self,
        session: AsyncSession,
        chamber_id: str,
        today: date,
    ):
        """
        Returns case summary + plan limits (no subscription join).
        """

        # 🔹 subquery using chamber snapshot
        max_cases_subq = (
            select(RefmPlanTypes.max_cases)
            .join(Chamber, Chamber.plan_code == RefmPlanTypes.code)
            .where(Chamber.chamber_id == chamber_id)
            .limit(1)
            .scalar_subquery()
        )

        stmt = select(
            func.count(Cases.case_id).label("total"),

            func.count(
                case(
                    (and_(
                        Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                        Cases.deleted_ind.is_(False)
                    ), 1),
                    else_=None
                )
            ).label("active"),

            func.count(
                case(
                    (and_(
                        Cases.status_code == RefmCaseStatusConstants.ADJOURNED,
                        Cases.deleted_ind.is_(False)
                    ), 1),
                    else_=None
                )
            ).label("adjourned"),

            func.count(
                case(
                    (and_(
                        Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                        Cases.next_hearing_date < today,
                        Cases.deleted_ind.is_(False)
                    ), 1),
                    else_=None
                )
            ).label("overdue"),

            # 🔥 plan limit (from chamber snapshot)
            max_cases_subq.label("max_cases")

        ).where(
            Cases.chamber_id == chamber_id,
            Cases.deleted_ind.is_(False)
        )

        result = await self.execute(session=session, stmt=stmt)
        return result.one()

    async def get_cases_by_status(
        self, session: AsyncSession
    ) -> List[dict]:
        """Cases grouped by status with descriptions and colors."""
        stmt = (
            select(
                Cases.status_code,
                RefmCaseStatus.description,
                RefmCaseStatus.color_code,
                func.count(Cases.case_id).label("count"),
            )
            .join(RefmCaseStatus, Cases.status_code == RefmCaseStatus.code)
            .group_by(
                Cases.status_code,
                RefmCaseStatus.description,
                RefmCaseStatus.color_code,
            )
        )

        rows = await self.execute(session=session, stmt=stmt)

        return [
            {
                "status_code": r.status_code,
                "status_description": r.description,
                "color_code": r.color_code,
                "count": r.count,
            }
            for r in rows
        ]

    async def get_cases_by_court(
        self, session: AsyncSession, limit: int = 10
    ) -> List[dict]:
        count_expr = func.count(Cases.case_id)

        stmt = (
            select(
                Cases.court_code,
                Courts.court_name,
                count_expr.label("cnt"),
            )
            .join(Courts, Cases.court_code == Courts.court_code)
            .group_by(Cases.court_code, Courts.court_name)
            .order_by(count_expr.desc())
            .limit(limit)
        )
        
        rows = await self.execute(
            session=session,
            stmt=stmt)
        return [{"court_code": r.court_code, "court_name": r.court_name, "count": r.cnt} for r in rows]

    async def get_cases_by_type(
        self, session: AsyncSession
    ) -> List[dict]:
        
        count_expr = func.count(Cases.case_id)

        stmt = (select(
            Cases.case_type_code,
            RefmCaseTypes.description,
            
            count_expr.label("cnt"),
        )
        .join(RefmCaseTypes, Cases.case_type_code == RefmCaseTypes.code)
        .where(
            Cases.case_type_code.isnot(None),
        )
        .group_by(Cases.case_type_code, RefmCaseTypes.description)
        .order_by(func.count(Cases.case_id).desc()))

        rows = await self.execute(
            session=session,
            stmt=stmt)

        return [{"case_type_code": r.case_type_code, "description": r.description, "count": r.cnt} for r in rows]

    async def count_cases_in_month(
        self,
        session: AsyncSession,
        month_start: date,
        month_end: date,
    ) -> int:
        stmt = select(func.count(Cases.case_id)).where(
                Cases.created_date >= month_start,
                Cases.created_date < month_end,
            )
        
        return await self.execute_scalar(session=session, stmt=stmt, default=0)

    async def count_cases_since(
        self,
        session: AsyncSession,
        since: date,
    ) -> int:
        stmt = select(func.count(Cases.case_id)).where(
                Cases.deleted_ind.is_(False),
                Cases.created_date >= since,
            )
        
        return await self.execute_scalar(session=session, stmt=stmt, default=0)
    
    async def list_cases_with_details(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        chamber_id: str,
        search: Optional[str] = None,
        status_code: Optional[str] = None,
        court_code: Optional[int] = None,
        sort_by: str = "updated_date",
    ):
        # ------------------------------------------------
        # 🔹 Latest Hearing (1 row per case)
        # ------------------------------------------------
        latest_hearing = (
            select(
                Hearings.case_id,
                Hearings.status_code,
                func.row_number().over(
                    partition_by=Hearings.case_id,
                    order_by=Hearings.hearing_date.desc(),
                ).label("rn"),
            )
            .where(
                Hearings.deleted_ind.is_(False),
                Hearings.chamber_id == chamber_id,
            )
            .subquery()
        )

        latest_hearing = (
            select(
                latest_hearing.c.case_id,
                latest_hearing.c.status_code,
            )
            .where(latest_hearing.c.rn == 1)
            .subquery()
        )

        # ------------------------------------------------
        # 🔹 Primary Client Role (1 row per case)
        # ------------------------------------------------
        primary_role = (
            select(
                CaseClients.case_id,
                CaseClients.party_role_code,
                CaseClients.case_client_id,
                func.row_number().over(
                    partition_by=CaseClients.case_id,
                    order_by=CaseClients.primary_ind.desc(),
                ).label("rn"),
            )
            .where(CaseClients.chamber_id == chamber_id)
            .subquery()
        )

        primary_role = (
            select(
                primary_role.c.case_id,
                primary_role.c.party_role_code,
                primary_role.c.case_client_id,
            )
            .where(primary_role.c.rn == 1)
            .subquery()
        )

        # ------------------------------------------------
        # 🔹 Primary AOR (1 row per case)
        # ------------------------------------------------
        aor_subq = (
            select(
                CaseAors.case_id,
                CaseAors.user_id,
                func.row_number().over(
                    partition_by=CaseAors.case_id,
                    order_by=CaseAors.appointment_date.asc(),
                ).label("rn"),
            )
            .where(
                CaseAors.primary_ind.is_(True),
                CaseAors.withdrawal_date.is_(None),
            )
            .subquery()
        )

        aor_subq = (
            select(aor_subq.c.case_id, aor_subq.c.user_id)
            .where(aor_subq.c.rn == 1)
            .subquery()
        )

        # ------------------------------------------------
        # 🔹 BASE QUERY (shared filters)
        # ------------------------------------------------
        base_filters = [
            Cases.deleted_ind.is_(False),
            Cases.chamber_id == chamber_id,
        ]

        if status_code and status_code.upper() != "ALL":
            base_filters.append(Cases.status_code == status_code.upper())

        if court_code:
            base_filters.append(Cases.court_code == court_code)

        if search and search.strip():
            kw = f"%{search.strip()}%"
            base_filters.append(
                or_(
                    Cases.case_number.ilike(kw),
                    Cases.petitioner.ilike(kw),
                    Cases.respondent.ilike(kw),
                )
            )

        # ------------------------------------------------
        # 🔹 RECORDS QUERY
        # ------------------------------------------------
        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                latest_hearing.c.status_code.label("hearing_status_code"),
                primary_role.c.party_role_code,
                primary_role.c.case_client_id,
                aor_subq.c.user_id.label("aor_user_id"),
            )
            .outerjoin(aor_subq, Cases.case_id == aor_subq.c.case_id)
            .outerjoin(Users, Users.user_id == aor_subq.c.user_id)
            .outerjoin(latest_hearing, Cases.case_id == latest_hearing.c.case_id)
            .outerjoin(primary_role, Cases.case_id == primary_role.c.case_id)
            .where(*base_filters)
        )

        # Sorting
        if sort_by == "hearing_date":
            stmt = stmt.order_by(Cases.next_hearing_date.asc())
        elif sort_by == "case_number":
            stmt = stmt.order_by(Cases.case_number.asc())
        else:
            stmt = stmt.order_by(Cases.updated_date.desc())

        # Pagination
        stmt = stmt.limit(limit).offset((page - 1) * limit)

        rows = (await self.execute(stmt=stmt, session=session)).all()

        # ------------------------------------------------
        # 🔹 COUNT QUERY (FIXED - EXACT MATCH)
        # ------------------------------------------------
        count_subq = (
            select(Cases.case_id)
            .outerjoin(aor_subq, Cases.case_id == aor_subq.c.case_id)
            .outerjoin(latest_hearing, Cases.case_id == latest_hearing.c.case_id)
            .outerjoin(primary_role, Cases.case_id == primary_role.c.case_id)
            .where(*base_filters)
            .subquery()
        )

        count_stmt = select(func.count()).select_from(count_subq)

        total = await self.execute_scalar(
            session=session,
            stmt=count_stmt,
            default=0,
        )

        return rows, total
    
    async def get_case_details(
        self,
        session: AsyncSession,
        case_id: str
    ):
        
        return await self.get_first(
            session=session,            
            where=[
                Cases.case_id == case_id,
            ]
        )
    
    async def list_cases_for_quick_hearing(
        self,
        session: AsyncSession,
        chamber_id: str,
        search: Optional[str] = None,
        limit: int = 50,
    ):
        primary_aor = (
            select(
                CaseAors.case_id,
                CaseAors.user_id,
                func.row_number().over(
                    partition_by=CaseAors.case_id,
                    order_by=CaseAors.appointment_date.asc(),
                ).label("rn"),
            )
            .where(
                CaseAors.chamber_id == chamber_id,
                CaseAors.primary_ind.is_(True),
                CaseAors.withdrawal_date.is_(None),
            )
            .subquery()
        )

        primary_aor = (
            select(primary_aor.c.case_id, primary_aor.c.user_id.label("aor_user_id"))
            .where(primary_aor.c.rn == 1)
            .subquery()
        )

        primary_role = (
            select(
                CaseClients.case_id,
                CaseClients.party_role_code,
                func.row_number().over(
                    partition_by=CaseClients.case_id,
                    order_by=CaseClients.primary_ind.desc(),
                ).label("rn"),
            )
            .where(CaseClients.chamber_id == chamber_id)
            .subquery()
        )

        primary_role = (
            select(primary_role.c.case_id, primary_role.c.party_role_code)
            .where(primary_role.c.rn == 1)
            .subquery()
        )

        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                primary_aor.c.aor_user_id,
                primary_role.c.party_role_code,
            )
            .outerjoin(primary_aor, Cases.case_id == primary_aor.c.case_id)
            .outerjoin(Users, Users.user_id == primary_aor.c.aor_user_id)
            .outerjoin(primary_role, Cases.case_id == primary_role.c.case_id)
            .where(
                Cases.chamber_id == chamber_id,
                Cases.deleted_ind.is_(False),
            )
        )

        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Cases.case_number.ilike(kw),
                    Cases.petitioner.ilike(kw),
                    Cases.respondent.ilike(kw),
                )
            )

        stmt = stmt.order_by(Cases.updated_date.desc()).limit(limit)
        
        result = await session.execute(stmt)
        return result.unique().all()
