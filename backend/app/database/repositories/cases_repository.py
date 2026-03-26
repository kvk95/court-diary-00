"""cases_repository.py — All DB operations for Cases"""

from datetime import date
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_case_types import RefmCaseTypes
from app.database.models.refm_courts import RefmCourts
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class CasesRepository(BaseRepository[Cases]):
    def __init__(self):
        super().__init__(Cases)

    async def get_case_summary_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
        active_code: str,
        adjourned_code: str,
        disposed_code: str,
        closed_code: str,
        today: date,
    ) -> dict:
        """All four stat-card counts in minimal DB round trips."""
        def _base():
            return select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
            )

        total = await session.scalar(_base()) or 0
        active = await session.scalar(_base().where(Cases.status_code == active_code)) or 0
        adjourned = await session.scalar(_base().where(Cases.status_code == adjourned_code)) or 0
        overdue = await session.scalar(
            _base().where(
                Cases.status_code == active_code,
                Cases.next_hearing_date < today,
            )
        ) or 0

        return {
            "total": total,
            "active": active,
            "adjourned": adjourned,
            "overdue": overdue,
        }

    async def get_cases_by_status(
        self, session: AsyncSession, chamber_id: str
    ) -> List[dict]:
        """Cases grouped by status with descriptions and colors."""
        rows = await session.execute(
            select(
                Cases.status_code,
                func.count(Cases.case_id).label("cnt"),
            )
            .where(Cases.chamber_id == chamber_id, Cases.is_deleted.is_(False))
            .group_by(Cases.status_code)
        )
        status_data = {r.status_code: r.cnt for r in rows}
        if not status_data:
            return []

        refm_rows = await session.execute(
            select(RefmCaseStatus.code, RefmCaseStatus.description, RefmCaseStatus.color_code)
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
        self, session: AsyncSession, chamber_id: str, limit: int = 10
    ) -> List[dict]:
        rows = await session.execute(
            select(
                Cases.court_id,
                RefmCourts.court_name,
                func.count(Cases.case_id).label("cnt"),
            )
            .join(RefmCourts, Cases.court_id == RefmCourts.court_id)
            .where(Cases.chamber_id == chamber_id, Cases.is_deleted.is_(False))
            .group_by(Cases.court_id, RefmCourts.court_name)
            .order_by(func.count(Cases.case_id).desc())
            .limit(limit)
        )
        return [{"court_id": r.court_id, "court_name": r.court_name, "count": r.cnt} for r in rows]

    async def get_cases_by_type(
        self, session: AsyncSession, chamber_id: str
    ) -> List[dict]:
        rows = await session.execute(
            select(
                Cases.case_type_code,
                RefmCaseTypes.description,
                func.count(Cases.case_id).label("cnt"),
            )
            .join(RefmCaseTypes, Cases.case_type_code == RefmCaseTypes.code)
            .where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.case_type_code.isnot(None),
            )
            .group_by(Cases.case_type_code, RefmCaseTypes.description)
            .order_by(func.count(Cases.case_id).desc())
        )
        return [{"case_type_code": r.case_type_code, "description": r.description, "count": r.cnt} for r in rows]

    async def count_cases_in_month(
        self,
        session: AsyncSession,
        chamber_id: str,
        month_start: date,
        month_end: date,
    ) -> int:
        return await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.created_date >= month_start,
                Cases.created_date < month_end,
            )
        ) or 0

    async def count_cases_since(
        self,
        session: AsyncSession,
        chamber_id: str,
        since: date,
    ) -> int:
        return await session.scalar(
            select(func.count(Cases.case_id)).where(
                Cases.chamber_id == chamber_id,
                Cases.is_deleted.is_(False),
                Cases.created_date >= since,
            )
        ) or 0
