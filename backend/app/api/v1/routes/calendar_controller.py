"""calendar_controller.py — HTTP routes for Calendar module"""

from datetime import date
from typing import List, Optional

from fastapi import Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.database.models.refm_hearing_status import RefmHearingStatusEnum
from app.dependencies import get_calendar_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.calendar_dto import CalendarEventOut, CalendarMonthOut
from app.services.calendar_service import CalendarService


class CalendarController(BaseController):
    CONTROLLER_NAME = "calendar"

    # ── Month view ────────────────────────────────────────────────────────

    @BaseController.get(
        "/month",
        summary="Get all hearings for a given month (calendar grid)",
        response_model=BaseOutDto[CalendarMonthOut],
    )
    async def calendar_get_month(
        self,
        year: int = Query(..., ge=2000, le=2099, description="Year e.g. 2026"),
        month: int = Query(..., ge=1, le=12, description="Month 1-12"),
        status_code: Optional[RefmHearingStatusEnum] = Query(None),
        service: CalendarService = Depends(get_calendar_service),  # read enforced in factory
    ) -> BaseOutDto[CalendarMonthOut]:
        return self.success(result=await service.calendar_get_month(
            year=year, month=month, status_code=status_code,
        ))

    # ── Upcoming widget ───────────────────────────────────────────────────

    @BaseController.get(
        "/upcoming",
        summary="Upcoming hearings (dashboard sidebar / widget)",
        response_model=BaseOutDto[List[CalendarEventOut]],
    )
    async def calendar_get_upcoming(
        self,
        days_ahead: int = Query(30, ge=1, le=365, description="Look-ahead window in days"),
        limit: int = Query(20, ge=1, le=100),
        service: CalendarService = Depends(get_calendar_service),  # read enforced in factory
    ) -> BaseOutDto[List[CalendarEventOut]]:
        return self.success(result=await service.calendar_get_upcoming(
            days_ahead=days_ahead, limit=limit,
        ))

    # ── Date range (week / agenda view) ──────────────────────────────────

    @BaseController.get(
        "/range",
        summary="Get hearings between two dates (week / agenda view)",
        response_model=BaseOutDto[List[CalendarEventOut]],
    )
    async def calendar_get_range(
        self,
        date_from: date = Query(..., description="Start date (inclusive) Example 2026-04-01"),
        date_to: date = Query(..., description="End date (inclusive) Example 2026-04-30"),
        status_code: Optional[RefmHearingStatusEnum] = Query(None),
        service: CalendarService = Depends(get_calendar_service),  # read enforced in factory
    ) -> BaseOutDto[List[CalendarEventOut]]:
        return self.success(result=await service.calendar_get_range(
            date_from=date_from, date_to=date_to, status_code=status_code,
        ))