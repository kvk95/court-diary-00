"""clients_dto.py — DTOs for Clients module"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional


from app.dtos.base.base_data import BaseInData, BaseRecordData
if TYPE_CHECKING:
    from app.dtos.cases_dto import CaseClientOut, CaseListOut
from app.dtos.users_dto import ImageInfoOut


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — List / Search / Detail
# ─────────────────────────────────────────────────────────────────────────────

class ClientDetailsOut(ImageInfoOut):
    """Slim DTO for Link Client modal search results."""    
    case_client_id: str
    client_id: str
    chamber_id: str
    client_type_code: str
    client_type_description: str
    party_type_code:str
    party_type_description: str
    client_name: str
    display_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    alternate_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    id_proof_code: Optional[str] = None
    id_proof_number: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None


class ClientListOut(ClientDetailsOut):
    linked_cases_count: int = 0

class ClientDetailOut(ClientListOut):
    linked_cases: List["CaseListOut"]
    # case_clients: List["CaseClientOut"]

class ClientSummaryStats(BaseRecordData):
    total: int
    parties: int
    individual: int
    corporate: int
    case_associations: int


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT — Create / Edit
# ─────────────────────────────────────────────────────────────────────────────

class ClientCreate(BaseInData):
    client_type_code: str
    party_type_code: str
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
    id_proof_code: Optional[str] = None
    id_proof_number: Optional[str] = None
    source_code: Optional[str] = None
    referral_source: Optional[str] = None
    client_since: Optional[date] = None
    notes: Optional[str] = None
    image_data: Optional[str]


class ClientEdit(ClientCreate):
    image_id: Optional[str]

class ClientNotesEdit(BaseInData):
    notes: str

from app.dtos.cases_dto import CaseListOut
ClientDetailOut.model_rebuild()