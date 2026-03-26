"""billing_dto.py — DTOs for Billing module (Bills, Payments, Documents)"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import field_validator

from app.dtos.base.base_data import BaseInData, BaseRecordData


# ─────────────────────────────────────────────────────────────────────────────
# BILL STATS
# ─────────────────────────────────────────────────────────────────────────────

class BillSummaryStats(BaseRecordData):
    total_billed: float = 0.0
    total_paid: float = 0.0
    total_outstanding: float = 0.0
    total_overdue: float = 0.0
    bill_count: int = 0
    overdue_count: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# BILLS — Out
# ─────────────────────────────────────────────────────────────────────────────

class BillListOut(BaseRecordData):
    bill_id: str
    bill_number: Optional[str] = None
    client_id: str
    client_name: str
    case_id: Optional[str] = ""
    case_number: Optional[str] = None
    bill_date: date
    due_date: Optional[date] = None
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    paid_amount: float = 0.0
    balance_amount: float = 0.0
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    color_code: Optional[str] = None
    created_date: Optional[datetime] = None


class BillDetailOut(BillListOut):
    service_description: Optional[str] = None
    notes: Optional[str] = None
    payments: List[dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# BILLS — In
# ─────────────────────────────────────────────────────────────────────────────

class BillCreate(BaseInData):
    client_id: str
    case_id: Optional[str] = None
    bill_number: Optional[str] = None
    bill_date: date
    due_date: Optional[date] = None
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    service_description: Optional[str] = None
    notes: Optional[str] = None
    status_code: str = "PN"

    @field_validator("amount", "total_amount")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)


class BillEdit(BaseInData):
    bill_id: str
    bill_number: Optional[str] = None
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    service_description: Optional[str] = None
    notes: Optional[str] = None
    status_code: Optional[str] = None


class BillDelete(BaseInData):
    bill_id: str


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENTS — Out
# ─────────────────────────────────────────────────────────────────────────────

class PaymentOut(BaseRecordData):
    payment_id: str
    bill_id: str
    client_id: str
    client_name: Optional[str] = None
    payment_date: date
    amount: float
    payment_mode: Optional[str] = None
    reference_no: Optional[str] = None
    bank_name: Optional[str] = None
    receipt_number: Optional[str] = None
    receipt_date: Optional[date] = None
    notes: Optional[str] = None
    created_date: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENTS — In
# ─────────────────────────────────────────────────────────────────────────────

class PaymentCreate(BaseInData):
    bill_id: str
    payment_date: date
    amount: float
    payment_mode: Optional[str] = None   # CASH | UPI | NEFT | CHQ | CARD
    reference_no: Optional[str] = None
    bank_name: Optional[str] = None
    receipt_number: Optional[str] = None
    receipt_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Payment amount must be greater than zero")
        return round(v, 2)


class PaymentDelete(BaseInData):
    payment_id: str


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTS — Out
# ─────────────────────────────────────────────────────────────────────────────

class DocumentOut(BaseRecordData):
    document_id: str
    client_id: str
    client_name: Optional[str] = None
    case_id: Optional[str] = None
    case_number: Optional[str] = None
    document_name: str
    document_type: Optional[str] = None
    document_category: Optional[str] = None
    received_date: Optional[date] = None
    received_from: Optional[str] = None
    returned_date: Optional[date] = None
    returned_to: Optional[str] = None
    custody_status: Optional[str] = None   # H=Held, R=Returned, L=Lost, D=Destroyed
    storage_location: Optional[str] = None
    file_number: Optional[str] = None
    notes: Optional[str] = None
    created_date: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTS — In
# ─────────────────────────────────────────────────────────────────────────────

class DocumentCreate(BaseInData):
    client_id: str
    case_id: Optional[str] = None
    document_name: str
    document_type: Optional[str] = None
    document_category: Optional[str] = None
    received_date: Optional[date] = None
    received_from: Optional[str] = None
    custody_status: str = "H"
    storage_location: Optional[str] = None
    file_number: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("document_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Document name is required")
        return v.strip()


class DocumentEdit(BaseInData):
    document_id: str
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    document_category: Optional[str] = None
    received_date: Optional[date] = None
    received_from: Optional[str] = None
    returned_date: Optional[date] = None
    returned_to: Optional[str] = None
    custody_status: Optional[str] = None
    storage_location: Optional[str] = None
    file_number: Optional[str] = None
    notes: Optional[str] = None
