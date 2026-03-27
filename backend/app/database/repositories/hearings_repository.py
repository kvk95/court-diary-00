"""hearings_repository.py — All DB operations for Hearings"""

from datetime import date, timedelta
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class HearingsRepository(BaseRepository[Hearings]):
    def __init__(self):
        super().__init__(Hearings)

    async def get_hearing_summary_stats(
        self,
        session: AsyncSession,
        chamber_id: str,
        today: date,
    ) -> dict:
        """All hearing stat-card counts in minimal queries."""
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)

        def _base():
            return select(func.count(Hearings.hearing_id)).where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
            )

        total = await session.scalar(_base()) or 0
        upcoming = await session.scalar(_base().where(Hearings.status_code.in_(["UP", "SC"]))) or 0
        completed = await session.scalar(_base().where(Hearings.status_code == "CMP")) or 0
        adjourned = await session.scalar(_base().where(Hearings.status_code == "ADJ")) or 0
        this_week = await session.scalar(
            _base().where(
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date >= today,
                Hearings.hearing_date <= week_end,
            )
        ) or 0
        this_month = await session.scalar(
            _base().where(
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date >= today,
                Hearings.hearing_date <= month_end,
            )
        ) or 0

        return {
            "total": total,
            "upcoming": upcoming,
            "completed": completed,
            "adjourned": adjourned,
            "this_week": this_week,
            "this_month": this_month,
        }

    async def count_hearings_in_month(
        self,
        session: AsyncSession,
        chamber_id: str,
        month_start: date,
        month_end: date,
        status_code: Optional[str] = None,
    ) -> int:
        conditions = [
            Hearings.chamber_id == chamber_id,
            Hearings.deleted_ind.is_(False),
            Hearings.hearing_date >= month_start,
            Hearings.hearing_date < month_end,
        ]
        if status_code:
            conditions.append(Hearings.status_code == status_code)
        return await session.scalar(
            select(func.count(Hearings.hearing_id)).where(*conditions)
        ) or 0

    async def get_calendar_events(
        self,
        session: AsyncSession,
        chamber_id: str,
        date_from: date,
        date_to: date,
    ) -> list:
        """
        All hearings in a date range with case + status info.
        Returns list of row objects with named attributes.
        """
        result = await session.execute(
            select(
                Hearings.hearing_id,
                Hearings.case_id,
                Hearings.hearing_date,
                Hearings.status_code,
                Hearings.purpose,
                Hearings.notes,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                Cases.court_id,
            )
            .join(Cases, Hearings.case_id == Cases.case_id)
            .where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),
                Hearings.hearing_date >= date_from,
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
        )
        return list(result.all())

    async def get_upcoming_hearings(
        self,
        session: AsyncSession,
        chamber_id: str,
        date_to: date,
        limit: int = 20,
    ) -> list:
        """Upcoming (UP/SC status) hearings up to date_to for sidebar widget."""
        result = await session.execute(
            select(
                Hearings.hearing_id,
                Hearings.case_id,
                Hearings.hearing_date,
                Hearings.status_code,
                Hearings.purpose,
                Cases.case_number,
                Cases.petitioner,
                Cases.respondent,
                Cases.court_id,
            )
            .join(Cases, Hearings.case_id == Cases.case_id)
            .where(
                Hearings.chamber_id == chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
            .limit(limit)
        )
        return list(result.all())

    async def get_status_map(self, session: AsyncSession) -> Tuple[dict, dict]:
        """Returns (description_map, color_map) keyed by status_code."""
        rows = await session.execute(
            select(
                RefmHearingStatus.code,
                RefmHearingStatus.description,
                RefmHearingStatus.color_code,
            )
        )
        desc_map: dict = {}
        color_map: dict = {}
        for r in rows:
            desc_map[r.code] = r.description
            color_map[r.code] = r.color_code
        return desc_map, color_map

    async def get_court_map(self, session: AsyncSession, court_ids: list) -> dict:
        if not court_ids:
            return {}
        rows = await session.execute(
            select(RefmCourts.court_id, RefmCourts.court_name)
            .where(RefmCourts.court_id.in_(court_ids))
        )
        return {r.court_id: r.court_name for r in rows}
