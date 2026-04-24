"""cases_dto.py — DTOs for Cases, Hearings, Case Notes, Case Clients"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import field_validator

from app.dtos.aor_dto import AorOut
from app.dtos.base.base_data import BaseInData, BaseRecordData
if TYPE_CHECKING:
    from app.dtos.clients_dto import ClientDetailsOut


# ─────────────────────────────────────────────────────────────────────────────
# CASES — List / Detail
# ─────────────────────────────────────────────────────────────────────────────

class CaseBasicInfoOut(BaseRecordData):
    case_id: str
    chamber_id: str
    case_number: str 
    court_code: str
    court_name: Optional[str] = None   
    case_type_code: Optional[str] = None
    case_type_description:Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: str
    respondent: str
    case_summary: Optional[str] = None
    status_code: Optional[str] = None
    status_description: Optional[str] = None

class CaseQuickHearingOut(CaseBasicInfoOut):
    aor_user_id: str
    aor_name: str
    party_role_code: str
    party_role_description: str

class CaseListOut(CaseQuickHearingOut):
    case_client_id: str
    next_hearing_date: Optional[date] = None
    last_hearing_date: Optional[date] = None
    next_hearing_status: Optional[str] = None
    updated_date: datetime


class CaseSummaryStats(BaseRecordData):
    total: int = 0
    active: int = 0
    adjourned: int = 0
    overdue: int = 0
    total_allowed: Optional[int] = None


# ─────────────────────────────────────────────────────────────────────────────
# CASES — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class CaseCreate(BaseInData):
    case_number: str
    court_code: str
    case_type_code: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: str
    respondent: str
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
    court_code: Optional[str] = None
    case_type_code: Optional[str] = None
    filing_year: Optional[int] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
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
    purpose_code: Optional[str] = None  
    purpose_description: Optional[str] = None
    notes: Optional[str] = None
    order_details: Optional[str] = None
    next_hearing_date: Optional[date] = None
    created_by_name: Optional[str] = None


class HearingCreate(BaseInData):
    case_id: str
    hearing_date: date
    status_code: str
    purpose_code: Optional[str] = None
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
    created_date: datetime


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
    chamber_id: str
    case_id: str
    client_id: str
    party_role_code: str
    party_role_description: str
    primary_ind: bool = False

class CaseClientLinkedOut(CaseClientOut):
    case_detail: "CaseListOut"
    client_detail: "ClientDetailsOut"


class CaseClientLinkPayload(BaseInData):
    client_id: str
    party_role_code: str
    primary_ind: bool = False

    @field_validator("party_role_code")
    @classmethod
    def party_role_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Party role is required")
        return v.strip().upper()


class CaseClientUnlinkPayload(BaseInData):
    case_client_id: str

# ─────────────────────────────────────────────────────────────────────────────
# CaseDetailOut moved to last as it should come after CaseClientOut
# ─────────────────────────────────────────────────────────────────────────────

class CaseDetailOut(CaseListOut):
    case_clients: List["CaseClientOut"]
    clients: List["ClientDetailsOut"]
    aor_details: List[AorOut]
    total_hearings: int = 0
    linked_clients: int = 0
    total_notes: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# RECENT ACTIVITY
# ─────────────────────────────────────────────────────────────────────────────

class RecentActivityItem(BaseRecordData):
    action: str
    actor_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    # 🔥 NEW (UI-friendly)
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None

from app.dtos.clients_dto import ClientDetailsOut
CaseClientLinkedOut.model_rebuild()
CaseDetailOut.model_rebuild()

# ─────────────────────────────────────────────────────────────────────────────
# Court Details
# ─────────────────────────────────────────────────────────────────────────────

class CourtItem(BaseRecordData):
    court_code: str
    court_name: str

    court_type_code: str
    court_type_name: str

    state_code: str | None
    state_name: str | None