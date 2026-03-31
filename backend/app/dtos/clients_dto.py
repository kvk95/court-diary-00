"""clients_dto.py — DTOs for Clients module"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData
from app.dtos.cases_dto import CaseListOut


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — List / Search / Detail
# ─────────────────────────────────────────────────────────────────────────────

class ClientSearchOut(BaseRecordData):
    """Slim DTO for Link Client modal search results."""
    client_id: str
    client_type_code: str
    client_type_description: str
    client_name: str
    contact_person: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    alternate_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    image_id: Optional[str] = None
    image_data: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None
    status_ind: bool = True
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


class ClientListOut(ClientSearchOut):
    linked_cases_count: int = 0
    created_date: Optional[datetime] = None


class ClientDetailOut(ClientListOut):
    chamber_id: str
    city: Optional[str] = None
    state_code: Optional[str] = None    
    linked_cases: List[CaseListOut] = []

class ClientSummaryStats(BaseRecordData):
    total: int
    active: int
    individual: int
    corporate: int
    case_associations: int


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class ClientCreate(BaseInData):
    client_type_code: str
    client_name: str
    display_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: str = "IN"
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("client_name")
    @classmethod
    def client_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Client name is required")
        return v.strip()


class ClientEdit(BaseInData):
    client_name: Optional[str] = None
    display_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None
    status_ind: Optional[bool] = None
