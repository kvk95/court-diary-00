"""cases_repository.py — All DB operations for Cases"""

from datetime import date
from typing import List, Optional

from sqlalchemy import and_, func, select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.case_aors import CaseAors
from app.database.models.case_clients import CaseClients
from app.database.models.cases import Cases
from app.database.models.refm_case_status import RefmCaseStatus, RefmCaseStatusConstants
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_courts import RefmCourts
from app.database.models.hearings import Hearings
from app.database.models.users import Users
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class CasesRepository(BaseRepository[Cases]):
    def __init__(self):
        super().__init__(Cases)

    async def get_case_summary_stats(
        self,
        session: AsyncSession,
        today: date,
    ) -> dict:
        """All four stat-card counts in minimal DB round trips."""
        def _base():
            stmt = select(func.count(Cases.case_id))
            return stmt

        stmt = _base()
        
        total = await self.execute_scalar(session=session, stmt=stmt, default=0)
        
        stmt = (stmt.where(Cases.status_code == RefmCaseStatusConstants.ACTIVE))
        active = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt = (stmt.where(Cases.status_code == RefmCaseStatusConstants.ADJOURNED))
        adjourned = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt = (
            stmt.where(
                Cases.status_code == RefmCaseStatusConstants.ACTIVE,
                Cases.next_hearing_date < today,
            )
        )
        overdue = self.execute_scalar(session=session, stmt=stmt, default=0)

        return {
            "total": total,
            "active": active,
            "adjourned": adjourned,
            "overdue": overdue,
        }
    
    async def get_case_summary(self,
        session: AsyncSession, 
        today,   
    ):
        row = await self.execute(
            session=session,
            stmt=select(
                func.count(Cases.case_id).label("total"),
                func.count(
                    case((Cases.status_code == RefmCaseStatusConstants.ACTIVE, Cases.case_id), else_=None)
                ).label("active"),
                func.count(
                    case((Cases.status_code == RefmCaseStatusConstants.ADJOURNED, Cases.case_id), else_=None)
                ).label("adjourned"),
                func.count(
                    case(
                        (
                            (Cases.status_code == RefmCaseStatusConstants.ACTIVE)
                            & (Cases.next_hearing_date < today),
                            Cases.case_id,
                        ),
                        else_=None,
                    )
                ).label("overdue"),
            )
        )
        r = row.one()
        return r

    async def get_cases_by_status(
        self, session: AsyncSession
    ) -> List[dict]:
        """Cases grouped by status with descriptions and colors."""
        stmt = (select(
                Cases.status_code,
                func.count(Cases.case_id).label("cnt"),
            )
            .group_by(Cases.status_code))
        
        rows =  (await self.execute( session=session, stmt=stmt)).all()
        status_data = {r.status_code: r.cnt for r in rows}
        if not status_data:
            return []

        refm_rows = await self.execute(
            session=session,
            stmt=select(RefmCaseStatus.code, RefmCaseStatus.description, RefmCaseStatus.color_code)
            .where(RefmCaseStatus.code.in_(list(status_data.keys())))
        )
        return [
            {
                "status_code": r.code,
                "status_description": r.description,
                "color_code": r.color_code,
                "count": status_data.get(r.code, 0),
            }
            for r in refm_rows
        ]

    async def get_cases_by_court(
        self, session: AsyncSession, limit: int = 10
    ) -> List[dict]:
        stmt = (select(
                Cases.court_id,
                RefmCourts.court_name,
                func.count(Cases.case_id).label("cnt"),
            )
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .group_by(Cases.court_id, RefmCourts.court_name)
            .order_by(func.count(Cases.case_id).desc())
            .limit(limit))
        
        rows = await self.execute(
            session=session,
            stmt=stmt)
        return [{"court_id": r.court_id, "court_name": r.court_name, "count": r.cnt} for r in rows]

    async def get_cases_by_type(
        self, session: AsyncSession
    ) -> List[dict]:
        stmt = (select(
            Cases.case_type_code,
            RefmCaseTypes.description,
            func.count(Cases.case_id).label("cnt"),
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
        court_id: Optional[int] = None,
        sort_by: str = "updated_date",
    ):
        # Latest hearing status per case
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
            select(latest_hearing.c.case_id, latest_hearing.c.status_code)
            .where(latest_hearing.c.rn == 1)
            .subquery()
        )

        # Primary client party role per case
        primary_role = (
            select(CaseClients.case_id, CaseClients.party_role_code)
            .where(
                CaseClients.chamber_id == chamber_id,
                CaseClients.primary_ind.is_(True),
            )
            .distinct(CaseClients.case_id)
            .subquery()
        )

        stmt = (
            select(
                Cases,
                Users.first_name,
                Users.last_name,
                latest_hearing.c.status_code.label("hearing_status_code"),
                primary_role.c.party_role_code,
                CaseAors.user_id.label("aor_user_id"),
            )
            .outerjoin(
                CaseAors,
                and_(
                    CaseAors.case_id == Cases.case_id,
                    CaseAors.primary_ind.is_(True),
                    CaseAors.withdrawal_date.is_(None),
                ),
            )
            .outerjoin(
                Users,
                Users.user_id == CaseAors.user_id,
            )
            .outerjoin(latest_hearing, Cases.case_id == latest_hearing.c.case_id)
            .outerjoin(primary_role, Cases.case_id == primary_role.c.case_id)
            .where(Cases.deleted_ind.is_(False))
        )

        if status_code and status_code.upper() != "ALL":
            stmt = stmt.where(Cases.status_code == status_code.upper())
        if court_id:
            stmt = stmt.where(Cases.court_id == court_id)
        if search and search.strip():
            kw = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Cases.case_number.ilike(kw),
                    Cases.petitioner.ilike(kw),
                    Cases.respondent.ilike(kw),
                )
            )

        if sort_by == "hearing_date":
            stmt = stmt.order_by(Cases.next_hearing_date.asc())
        elif sort_by == "case_number":
            stmt = stmt.order_by(Cases.case_number.asc())
        else:
            stmt = stmt.order_by(Cases.updated_date.desc())

        stmt = stmt.limit(limit).offset((page - 1) * limit)
        rows = (await self.execute(stmt=stmt, session=session)).all()

        count_stmt = (
            select(func.count())
            .select_from(Cases)
            .where(Cases.deleted_ind.is_(False), Cases.chamber_id == chamber_id)
        )
        total = await self.execute_scalar(session=session, stmt=count_stmt, default=0)

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
        search: Optional[str] = None,
        limit: int = 50,
    ):
        # One row per case — primary AOR user
        # MIN(user_id) satisfies only_full_group_by while still picking one user
        primary_aor = (
            select(
                CaseAors.case_id,
                func.min(CaseAors.user_id).label("aor_user_id"),
            )
            .where(
                CaseAors.primary_ind.is_(True),
                CaseAors.withdrawal_date.is_(None),
            )
            .group_by(CaseAors.case_id)
            .subquery()
        )

        # One row per case — primary client party role
        primary_role = (
            select(
                CaseClients.case_id,
                func.min(CaseClients.party_role_code).label("party_role_code"),
            )
            .where(CaseClients.primary_ind.is_(True))
            .group_by(CaseClients.case_id)
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

        rows = (await self.execute(session=session, stmt=stmt)).all()
        return rows
