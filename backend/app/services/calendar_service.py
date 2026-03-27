"""calendar_service.py — Business logic only; all DB queries delegated to HearingsRepository"""

from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

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

    def _make_title(self, case_number: str, purpose: Optional[str]) -> str:
        return f"{case_number} — {purpose}" if purpose else case_number

    def _make_event(self, r, court_map: dict, desc_map: dict, color_map: dict) -> CalendarEventOut:
        return CalendarEventOut(
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

    # ─────────────────────────────────────────────────────────────────────
    # MONTH VIEW
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_month(self, year: int, month: int) -> CalendarMonthOut:
        from calendar import monthrange
        _, last_day = monthrange(year, month)
        date_from = date(year, month, 1)
        date_to = date(year, month, last_day)

        hearing_rows = await self.hearings_repo.get_calendar_events(
            session=self.session,
            chamber_id=self.chamber_id,
            date_from=date_from,
            date_to=date_to,
        )

        desc_map, color_map = await self.hearings_repo.get_status_map(session=self.session)
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self.hearings_repo.get_court_map(session=self.session, court_ids=court_ids)

        events = [self._make_event(r, court_map, desc_map, color_map) for r in hearing_rows]

        upcoming_count = sum(1 for e in events if e.status_code in ("UP", "SC"))
        completed_count = sum(1 for e in events if e.status_code == "CMP")

        return CalendarMonthOut.model_validate({
            "year": year,
            "month": month,
            "events": events,
            "total_hearings": len(events),
            "upcoming_count": upcoming_count,
            "completed_count": completed_count,
        })

    # ─────────────────────────────────────────────────────────────────────
    # UPCOMING WIDGET
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_upcoming(
        self,
        days_ahead: int = 30,
        limit: int = 20,
    ) -> List[CalendarUpcomingOut]:
        today = date.today()
        date_to = today + timedelta(days=days_ahead)

        hearing_rows = await self.hearings_repo.get_upcoming_hearings(
            session=self.session,
            chamber_id=self.chamber_id,
            date_to=date_to,
            limit=limit,
        )

        _, color_map = await self.hearings_repo.get_status_map(session=self.session)
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self.hearings_repo.get_court_map(session=self.session, court_ids=court_ids)

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
    # DATE RANGE
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_range(
        self,
        date_from: date,
        date_to: date,
    ) -> List[CalendarEventOut]:
        hearing_rows = await self.hearings_repo.get_calendar_events(
            session=self.session,
            chamber_id=self.chamber_id,
            date_from=date_from,
            date_to=date_to,
        )

        desc_map, color_map = await self.hearings_repo.get_status_map(session=self.session)
        court_ids = list({r.court_id for r in hearing_rows if r.court_id})
        court_map = await self.hearings_repo.get_court_map(session=self.session, court_ids=court_ids)

        return [self._make_event(r, court_map, desc_map, color_map) for r in hearing_rows]
