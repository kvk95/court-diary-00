"""calendar_dto.py — DTOs for Calendar module"""

from datetime import date
from typing import List, Optional

from app.dtos.base.base_data import BaseRecordData


class CalendarEventOut(BaseRecordData):
    """One event on the calendar grid — always a hearing in the current schema."""
    event_id: str                        # "hearing:{id}"
    event_type: str = "hearing"
    title: str                           # e.g. "WP.No.1234/2024 — Arguments"
    case_id: str
    case_number: str
    hearing_id: str
    event_date: date
    court_name: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    color: Optional[str] = None          # hex from refm_hearing_status.color_code


class CalendarMonthOut(BaseRecordData):
    """All hearings for a requested month, keyed by date for the UI grid."""
    year: int
    month: int
    events: List[CalendarEventOut] = []
    total_hearings: int = 0
    upcoming_count: int = 0
    completed_count: int = 0


class CalendarUpcomingOut(BaseRecordData):
    """Slim row for the upcoming-hearings widget / dashboard sidebar."""
    hearing_id: str
    case_id: str
    case_number: str
    petitioner: str
    respondent: str
    court_name: Optional[str] = None
    hearing_date: date
    days_until: int                      # 0 = today, negative = overdue
    purpose: Optional[str] = None
    status_code: Optional[str] = None
    color: Optional[str] = None
