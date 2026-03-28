"""cases_dto.py — DTOs for Cases, Hearings, Case Notes, Case Clients"""

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# CASES — List / Detail
# ─────────────────────────────────────────────────────────────────────────────

class CaseListOut(BaseRecordData):
    case_id: str
    chamber_id: str
    case_number: str 
    court_id: int
    court_name: Optional[str] = None   
    case_type_code: Optional[str] = None
    case_type_description:Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: str
    respondent: str
    aor_user_id: Optional[str] = None
    aor_name: Optional[str] = None
    case_summary: Optional[str] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    next_hearing_date: Optional[date] = None
    last_hearing_date: Optional[date] = None


class CaseDetailOut(CaseListOut):
    total_hearings: int = 0
    linked_clients: int = 0
    total_notes: int = 0


class CaseSummaryStats(BaseRecordData):
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
    aor_user_id: Optional[str] = None
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
    case_id: str
    case_number: Optional[str] = None
    court_id: Optional[int] = None
    case_type_code: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    aor_user_id: Optional[str] = None
    case_summary: Optional[str] = None
    status_code: Optional[str] = None
    next_hearing_date: Optional[date] = None


class CaseDelete(BaseInData):
    case_id: str


# ─────────────────────────────────────────────────────────────────────────────
# HEARINGS
# ─────────────────────────────────────────────────────────────────────────────

class HearingOut(BaseRecordData):
    hearing_id: str
    case_id: str
    hearing_date: date
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None
    created_by_name: Optional[str] = None


class HearingCreate(BaseInData):
    case_id: str
    hearing_date: date
    status_code: str
    purpose: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None


class HearingEdit(HearingCreate):
    hearing_id: str


class HearingDelete(BaseInData):
    hearing_id: str


# ─────────────────────────────────────────────────────────────────────────────
# CASE NOTES
# ─────────────────────────────────────────────────────────────────────────────

class CaseNoteOut(BaseRecordData):
    note_id: str
    case_id: str
    user_id: str
    author_name: Optional[str] = None
    note_text: str
    private_ind: bool = False


class CaseNoteCreate(BaseInData):
    case_id: str
    note_text: str
    private_ind: bool = False

    @field_validator("note_text")
    @classmethod
    def note_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Note text is required")
        return v.strip()


class CaseNoteEdit(CaseNoteCreate):
    note_id: str


class CaseNoteDelete(BaseInData):
    note_id: str


# ─────────────────────────────────────────────────────────────────────────────
# CASE CLIENTS (link client to case)
# ─────────────────────────────────────────────────────────────────────────────

class CaseClientOut(BaseRecordData):
    case_client_id: str
    client_id: str
    client_name: str
    client_type: str
    party_role: str
    party_role_description: Optional[str] = None
    primary_ind: bool = False
    engagement_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CaseClientLinkPayload(BaseInData):
    client_id: str
    party_role: str
    primary_ind: bool = False
    engagement_type: Optional[str] = None

    @field_validator("party_role")
    @classmethod
    def party_role_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Party role is required")
        return v.strip().upper()


class CaseClientUnlinkPayload(BaseInData):
    case_client_id: str


# ─────────────────────────────────────────────────────────────────────────────
# RECENT ACTIVITY
# ─────────────────────────────────────────────────────────────────────────────

class RecentActivityItem(BaseRecordData):
    action: str
    actor_name: Optional[str] = None
    timestamp: Optional[datetime] = None
