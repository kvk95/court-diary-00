"""calendar_service.py — Business logic only; all DB queries delegated to HearingsRepository"""

from calendar import monthrange
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_courts import RefmCourts
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_hearing_status import RefmHearingStatus, RefmHearingStatusConstants
from app.database.repositories.hearings_repository import HearingsRepository
from app.dtos.calendar_dto import CalendarEventOut, CalendarMonthOut
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

    def _make_event(self, r, refm_maps ) -> CalendarEventOut:
        desc_map, color_map, court_map, purpose_map = refm_maps
        return CalendarEventOut(
            event_id=f"hearing:{r.hearing_id}",
            event_type="hearing",
            title=self._make_title(r.case_number, purpose_map.get(r.purpose_code) if r.purpose_code else None),
            case_id=r.case_id,
            case_number=r.case_number,
            hearing_id=r.hearing_id,
            event_date=r.hearing_date,
            court_name=court_map.get(r.court_id),
            petitioner=r.petitioner,
            respondent=r.respondent,
            status_code=r.status_code,
            status_description=desc_map.get(r.status_code) if r.status_code else None,            
            purpose_code=r.purpose_code,
            purpose_description=purpose_map.get(r.purpose_code) if r.purpose_code else None,
            notes=r.notes,
            color=color_map.get(r.status_code) if r.status_code else None,
        )
    
    async def _load_maps(self):
        if hasattr(self, "_maps_cache"):
            return self._maps_cache

        desc_map = await self.refm_resolver.get_desc_map(
            column_attr=Hearings.status_code,
            value_column=RefmHearingStatus.description)
        color_map = await self.refm_resolver.get_desc_map(
            column_attr=Hearings.status_code,
            value_column=RefmHearingStatus.color_code)
        court_map = await self.refm_resolver.get_desc_map(
            column_attr=Cases.court_id,
            value_column=RefmCourts.court_name)
        purpose_map = await self.refm_resolver.get_desc_map(
            column_attr=Hearings.purpose_code,
            value_column=RefmHearingPurpose.description,
        )

        self._maps_cache = (desc_map, color_map, court_map, purpose_map)
        return self._maps_cache

    # ─────────────────────────────────────────────────────────────────────
    # MONTH VIEW
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_month(self, 
                                 year: int, 
                                 month: int,
                                 status_code: Optional[str] = None,) -> CalendarMonthOut:
        
        _, last_day = monthrange(year, month)
        date_from = date(year, month, 1)
        date_to = date(year, month, last_day)

        hearing_rows = await self.hearings_repo.get_calendar_events(
            session=self.session,
            date_from=date_from,
            date_to=date_to,
            status_code = status_code,
        )

        refm_maps = await self._load_maps()

        events = []
        upcoming_count = completed_count = 0

        for r in hearing_rows:
            e = self._make_event(r, refm_maps)
            events.append(e)
            if e.status_code in (RefmHearingStatusConstants.UPCOMING, RefmHearingStatusConstants.SCHEDULED):
                upcoming_count += 1
            elif e.status_code == RefmHearingStatusConstants.COMPLETED:
                completed_count += 1

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
    ) -> List[CalendarEventOut]:
        today = date.today()
        date_to = today + timedelta(days=days_ahead)

        hearing_rows = await self.hearings_repo.get_upcoming_hearings(
            session=self.session,
            date_to=date_to,
            limit=limit,
        )

        refm_maps = await self._load_maps()

        return [self._make_event(r, refm_maps) for r in hearing_rows]

    # ─────────────────────────────────────────────────────────────────────
    # DATE RANGE
    # ─────────────────────────────────────────────────────────────────────

    async def calendar_get_range(
        self,
        date_from: date,
        date_to: date,
        status_code: Optional[str] = None,
    ) -> List[CalendarEventOut]:
        hearing_rows = await self.hearings_repo.get_calendar_events(
            session=self.session,
            date_from=date_from,
            date_to=date_to,
            status_code=status_code,
        )

        refm_maps = await self._load_maps()
        return [self._make_event(r, refm_maps) for r in hearing_rows]
