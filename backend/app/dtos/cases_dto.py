# app\dtos\cases_dto.py

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# COURT (reference — used inside case responses)
# ─────────────────────────────────────────────────────────────────────────────

class CourtOut(BaseRecordData):
    court_id: int
    court_name: str


# ─────────────────────────────────────────────────────────────────────────────
# CASES — List / Detail
# ─────────────────────────────────────────────────────────────────────────────

class CaseListOut(BaseRecordData):
    """Compact row shown in the Cases list screen."""
    case_id: int
    case_number: str
    status_code: Optional[str] = None
    court_name: Optional[str] = None          # joined from refm_courts
    petitioner: str
    respondent: str
    aor_name: Optional[str] = None            # joined from users (first_name + last_name)
    next_hearing_date: Optional[date] = None
    updated_date: Optional[datetime] = None


class CaseDetailOut(BaseRecordData):
    """Full case detail for the Case Detail screen."""
    case_id: int
    chamber_id: int
    case_number: str
    court_id: int
    court_name: Optional[str] = None
    case_type_code: Optional[str] = None
    case_type_description: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: str
    respondent: str
    aor_user_id: Optional[int] = None
    aor_name: Optional[str] = None
    case_summary: Optional[str] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    next_hearing_date: Optional[date] = None
    last_hearing_date: Optional[date] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    # Counts for overview panel
    total_hearings: int = 0
    linked_clients: int = 0
    total_notes: int = 0


class CaseSummaryStats(BaseRecordData):
    """Stats for the top-of-page stat cards."""
    total: int = 0
    active: int = 0
    adjourned: int = 0
    overdue: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# CASES — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class CaseCreate(BaseInData):
    case_number: str
    court_id: int
    case_type_code: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: str
    respondent: str
    aor_name: Optional[str] = None            # free-text AOR (stored in petitioner/respondent or used to find user)
    aor_user_id: Optional[int] = None
    case_summary: Optional[str] = None
    status_code: str = "AC"
    next_hearing_date: Optional[date] = None

    @field_validator("case_number")
    @classmethod
    def case_number_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Case number is required")
        return v.strip()

    @field_validator("petitioner")
    @classmethod
    def petitioner_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Petitioner is required")
        return v.strip()

    @field_validator("respondent")
    @classmethod
    def respondent_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Respondent is required")
        return v.strip()


class CaseEdit(BaseInData):
    case_id: int
    case_number: Optional[str] = None
    court_id: Optional[int] = None
    case_type_code: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    aor_user_id: Optional[int] = None
    case_summary: Optional[str] = None
    status_code: Optional[str] = None
    next_hearing_date: Optional[date] = None


class CaseDelete(BaseInData):
    case_id: int


# ─────────────────────────────────────────────────────────────────────────────
# HEARINGS — List / Detail
# ─────────────────────────────────────────────────────────────────────────────

class HearingOut(BaseRecordData):
    """Single hearing record — used in hearing history list."""
    hearing_id: int
    case_id: int
    hearing_date: date
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None
    created_by_name: Optional[str] = None     # user who created/recorded this hearing
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# HEARINGS — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class HearingCreate(BaseInData):
    case_id: int
    hearing_date: date
    status_code: str = "SC"                   # SC=Scheduled by default
    purpose: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None


class HearingEdit(BaseInData):
    hearing_id: int
    hearing_date: Optional[date] = None
    status_code: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None


class HearingDelete(BaseInData):
    hearing_id: int


# ─────────────────────────────────────────────────────────────────────────────
# CASE NOTES — List / Detail
# ─────────────────────────────────────────────────────────────────────────────

class CaseNoteOut(BaseRecordData):
    note_id: int
    case_id: int
    user_id: int
    author_name: Optional[str] = None         # first_name + last_name of user
    note_text: str
    is_private: bool = False
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# CASE NOTES — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class CaseNoteCreate(BaseInData):
    case_id: int
    note_text: str
    is_private: bool = False

    @field_validator("note_text")
    @classmethod
    def note_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Note text is required")
        return v.strip()


class CaseNoteEdit(BaseInData):
    note_id: int
    note_text: Optional[str] = None
    is_private: Optional[bool] = None


class CaseNoteDelete(BaseInData):
    note_id: int


# ─────────────────────────────────────────────────────────────────────────────
# ACTIVITY LOG — Recent activity shown in sidebar of case detail
# ─────────────────────────────────────────────────────────────────────────────

class RecentActivityItem(BaseRecordData):
    action: str
    actor_name: Optional[str] = None
    timestamp: Optional[datetime] = None