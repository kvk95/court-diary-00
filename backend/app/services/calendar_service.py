"""calendar_service.py — Business logic for Calendar module"""

from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.repositories.hearings_repository import HearingsRepository
from app.dtos.calendar_dto import CalendarEventOut, CalendarMonthOut, CalendarUpcomingOut
from app.services.base.secured_base_service import BaseSecuredService


class CalendarService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        hearings_repo: Optional[HearingsRepository] = None,
    ):
        super().__init__(session)
        self.hearings_repo = hearings_repo or HearingsRepository()

    # ─────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────────────────────

    async def _load_status_map(self) -> tuple[dict, dict]:
        """Returns (description_map, color_map) keyed by status_code."""
        rows = await self.session.execute(
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

    async def _load_court_map(self, court_ids: list) -> dict:
        if not court_ids:
            return {}
        rows = await self.session.execute(
            select(RefmCourts.court_id, RefmCourts.court_name)
            .where(RefmCourts.court_id.in_(court_ids))
        )
        return {r.court_id: r.court_name for r in rows}

    def _make_title(self, case_number: str, purpose: Optional[str]) -> str:
        return f"{case_number} — {purpose}" if purpose else case_number

    # ─────────────────────────────────────────────────────────────────────
    # MONTH VIEW
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_month(self, year: int, month: int) -> CalendarMonthOut:
        """All hearings in a given month for this chamber."""
        # Build date range — first and last day of the month
        from calendar import monthrange
        _, last_day = monthrange(year, month)
        date_from = date(year, month, 1)
        date_to = date(year, month, last_day)

        rows = await self.session.execute(
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
                Hearings.chamber_id == self.chamber_id,
                Hearings.is_deleted.is_(False),
                Cases.is_deleted.is_(False),
                Hearings.hearing_date >= date_from,
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
        )
        hearing_rows = rows.fetchall()

        desc_map, color_map = await self._load_status_map()
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self._load_court_map(court_ids)

        events: List[CalendarEventOut] = [
            CalendarEventOut(
                event_id=f"hearing:{r.hearing_id}",
                event_type="hearing",
                title=self._make_title(r.case_number, r.purpose),
                case_id=r.case_id,
                case_number=r.case_number,
                hearing_id=r.hearing_id,
                event_date=r.hearing_date,
                court_name=court_map.get(r.court_id),
                petitioner=r.petitioner,
                respondent=r.respondent,
                status_code=r.status_code,
                status_description=desc_map.get(r.status_code) if r.status_code else None,
                purpose=r.purpose,
                notes=r.notes,
                color=color_map.get(r.status_code) if r.status_code else None,
            )
            for r in hearing_rows
        ]

        upcoming_count = sum(
            1 for e in events
            if e.status_code in ("UP", "SC")
        )
        completed_count = sum(
            1 for e in events
            if e.status_code == "CMP"
        )

        return CalendarMonthOut(
            year=year,
            month=month,
            events=events,
            total_hearings=len(events),
            upcoming_count=upcoming_count,
            completed_count=completed_count,
        )

    # ─────────────────────────────────────────────────────────────────────
    # UPCOMING — Dashboard widget / sidebar
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_upcoming(
        self,
        days_ahead: int = 30,
        limit: int = 20,
    ) -> List[CalendarUpcomingOut]:
        """Hearings in the next N days (plus any overdue), ordered by date."""
        today = date.today()
        date_to = today + timedelta(days=days_ahead)

        rows = await self.session.execute(
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
                Hearings.chamber_id == self.chamber_id,
                Hearings.is_deleted.is_(False),
                Cases.is_deleted.is_(False),
                Hearings.status_code.in_(["UP", "SC"]),
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
            .limit(limit)
        )
        hearing_rows = rows.fetchall()

        _, color_map = await self._load_status_map()
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self._load_court_map(court_ids)

        return [
            CalendarUpcomingOut(
                hearing_id=r.hearing_id,
                case_id=r.case_id,
                case_number=r.case_number,
                petitioner=r.petitioner,
                respondent=r.respondent,
                court_name=court_map.get(r.court_id),
                hearing_date=r.hearing_date,
                days_until=(r.hearing_date - today).days,
                purpose=r.purpose,
                status_code=r.status_code,
                color=color_map.get(r.status_code) if r.status_code else None,
            )
            for r in hearing_rows
        ]

    # ─────────────────────────────────────────────────────────────────────
    # DATE RANGE — For custom date-picker queries
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_range(
        self,
        date_from: date,
        date_to: date,
    ) -> List[CalendarEventOut]:
        """All hearings between two dates (for week/agenda views)."""
        rows = await self.session.execute(
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
                Hearings.chamber_id == self.chamber_id,
                Hearings.is_deleted.is_(False),
                Cases.is_deleted.is_(False),
                Hearings.hearing_date >= date_from,
                Hearings.hearing_date <= date_to,
            )
            .order_by(Hearings.hearing_date.asc())
        )
        hearing_rows = rows.fetchall()

        desc_map, color_map = await self._load_status_map()
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self._load_court_map(court_ids)

        return [
            CalendarEventOut(
                event_id=f"hearing:{r.hearing_id}",
                event_type="hearing",
                title=self._make_title(r.case_number, r.purpose),
                case_id=r.case_id,
                case_number=r.case_number,
                hearing_id=r.hearing_id,
                event_date=r.hearing_date,
                court_name=court_map.get(r.court_id),
                petitioner=r.petitioner,
                respondent=r.respondent,
                status_code=r.status_code,
                status_description=desc_map.get(r.status_code) if r.status_code else None,
                purpose=r.purpose,
                notes=r.notes,
                color=color_map.get(r.status_code) if r.status_code else None,
            )
            for r in hearing_rows
        ]
