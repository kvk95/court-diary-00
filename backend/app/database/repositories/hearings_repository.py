"""hearings_repository.py — All DB operations for Hearings"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_hearing_status import RefmHearingStatusConstants
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
        
        stmt = _base()
        total = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt = stmt.where(Hearings.status_code.in_([RefmHearingStatusConstants.UPCOMING, RefmHearingStatusConstants.SCHEDULED]))
        upcoming = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt = stmt.where(Hearings.status_code == RefmHearingStatusConstants.COMPLETED)
        completed = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt = stmt.where(Hearings.status_code == RefmHearingStatusConstants.ADJOURNED)
        adjourned = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt =  stmt.where(
                Hearings.status_code.in_([RefmHearingStatusConstants.UPCOMING, RefmHearingStatusConstants.SCHEDULED]),
                Hearings.hearing_date.between(today, week_end),
            )
        this_week = await self.execute_scalar(session=session, stmt=stmt, default=0)

        stmt =  stmt.where(
                Hearings.status_code.in_([RefmHearingStatusConstants.UPCOMING, RefmHearingStatusConstants.SCHEDULED]),
                Hearings.hearing_date.between(today, week_end),
            )
        this_month = await self.execute_scalar(session=session, stmt=stmt, default=0)

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
            Hearings.hearing_date.between(month_start, month_end)
        ]
        if status_code:
            conditions.append(Hearings.status_code == status_code)
        return await self.execute_scalar( session=session, stmt=
            select(func.count(Hearings.hearing_id)).where(*conditions)
        )
    
    def _base_hearing_query(self):
        return select(
            Hearings.hearing_id,
            Hearings.case_id,
            Hearings.hearing_date,
            Hearings.status_code,
            Hearings.purpose_code,
            Hearings.notes,
            Cases.case_number,
            Cases.petitioner,
            Cases.respondent,
            Cases.court_code,
        ).join(Cases, Hearings.case_id == Cases.case_id)

    async def get_calendar_events(
        self,
        session: AsyncSession,
        date_from: date,
        date_to: date,
        status_code: Optional[str] = None,
    ) -> list:
        """
        All hearings in a date range with case + status info.
        Returns list of row objects with named attributes.
        """
        stmt= self._base_hearing_query().where(
            Hearings.chamber_id == self.chamber_id,
            Hearings.deleted_ind.is_(False),
            Cases.deleted_ind.is_(False),
            Hearings.hearing_date.between(date_from, date_to),
            ).order_by(Hearings.hearing_date.asc())        
        
        if status_code:
            stmt = stmt.where(Hearings.status_code == status_code)
        
        result = await self.execute( session=session, stmt=stmt);
        return list(result.all())

    async def get_upcoming_hearings(
        self,
        session: AsyncSession,
        date_to: date,
        limit: int = 20,
    ) -> list:
        """Upcoming (UP/SC status) hearings up to date_to for sidebar widget."""
        result = await self.execute( session=session, stmt=
            self._base_hearing_query()
            .where(
                Hearings.chamber_id == self.chamber_id,
                Hearings.deleted_ind.is_(False),
                Cases.deleted_ind.is_(False),
                Hearings.status_code.in_([RefmHearingStatusConstants.UPCOMING, RefmHearingStatusConstants.SCHEDULED]),
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
            .limit(limit)
        )
        return list(result.all())
