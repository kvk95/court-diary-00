"""client_bills"""

from sqlalchemy import ForeignKey, CHAR, Date, Numeric, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ClientBills(BaseModel, TimestampMixin):
    __tablename__ = 'client_bills'

    # bill_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    bill_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="SET NULL"))

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # bill_number : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    bill_number: Mapped[Optional[str]] = mapped_column(String(50))

    # bill_date : DATE
    bill_date: Mapped[date] = mapped_column(Date, nullable=False)

    # due_date : DATE
    due_date: Mapped[Optional[date]] = mapped_column(Date)

    # amount : DECIMAL(12, 2)
    amount: Mapped[float] = mapped_column(Numeric, nullable=False)

    # tax_amount : DECIMAL(12, 2)
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric, default='0.00')

    # total_amount : DECIMAL(12, 2)
    total_amount: Mapped[float] = mapped_column(Numeric, nullable=False)

    # paid_amount : DECIMAL(12, 2)
    paid_amount: Mapped[Optional[float]] = mapped_column(Numeric, default='0.00')

    # balance_amount : DECIMAL(12, 2)
    balance_amount: Mapped[Optional[float]] = mapped_column(Numeric)

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_billing_status.code", ondelete="SET NULL"), default='BSPN')

    # service_description : TEXT COLLATE "utf8mb4_unicode_ci"
    service_description: Mapped[Optional[str]] = mapped_column(Text)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_bills.chamber_id -> chamber.chamber_id
    client_bills_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("client_bills_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # client_bills.case_id -> cases.case_id
    client_bills_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("client_bills_case_id_casess", cascade="all, delete-orphan")
    )

    # client_bills.client_id -> clients.client_id
    client_bills_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("client_bills_client_id_clientss", cascade="all, delete-orphan")
    )

    # client_bills.status_code -> refm_billing_status.code
    client_bills_status_code_refm_billing_status = relationship(
        "RefmBillingStatus",
        foreign_keys=[status_code], 
        backref=backref("client_bills_status_code_refm_billing_statuss", cascade="all, delete-orphan")
    )

    # client_bills.created_by -> users.user_id
    client_bills_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_bills_created_by_userss", cascade="all, delete-orphan")
    )

    # client_bills.updated_by -> users.user_id
    client_bills_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("client_bills_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

