"""clients_dto.py — DTOs for Clients module"""

from datetime import date, datetime
from typing import Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — List / Search / Detail
# ─────────────────────────────────────────────────────────────────────────────

class ClientSearchOut(BaseRecordData):
    """Slim DTO for Link Client modal search results."""
    client_id: int
    client_name: str
    display_name: Optional[str] = None
    client_type: str
    phone: Optional[str] = None
    email: Optional[str] = None


class ClientListOut(BaseRecordData):
    client_id: int
    client_type: str
    client_name: str
    display_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    status_ind: bool = True
    linked_cases: int = 0
    created_date: Optional[datetime] = None


class ClientDetailOut(BaseRecordData):
    client_id: int
    chamber_id: int
    client_type: str
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
    country_code: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None
    status_ind: bool = True
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    linked_cases: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class ClientCreate(BaseInData):
    client_type: str = "I"  # I=Individual, O=Organization
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

    @field_validator("client_type")
    @classmethod
    def client_type_valid(cls, v: str) -> str:
        if v not in ("I", "O"):
            raise ValueError("client_type must be 'I' (Individual) or 'O' (Organization)")
        return v


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
