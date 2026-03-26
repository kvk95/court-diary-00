"""client_payments"""

from sqlalchemy import ForeignKey, CHAR, Date, Numeric, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ClientPayments(BaseModel, TimestampMixin):
    __tablename__ = 'client_payments'

    # payment_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    payment_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # bill_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    bill_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("client_bills.bill_id", ondelete="CASCADE"), nullable=False)

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # payment_date : DATE
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)

    # amount : DECIMAL(12, 2)
    amount: Mapped[float] = mapped_column(Numeric, nullable=False)

    # payment_mode : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    payment_mode: Mapped[Optional[str]] = mapped_column(String(20))

    # reference_no : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    reference_no: Mapped[Optional[str]] = mapped_column(String(100))

    # bank_name : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))

    # receipt_number : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    receipt_number: Mapped[Optional[str]] = mapped_column(String(50))

    # receipt_date : DATE
    receipt_date: Mapped[Optional[date]] = mapped_column(Date)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_payments.chamber_id -> chamber.chamber_id
    client_payments_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("client_payments_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # client_payments.bill_id -> client_bills.bill_id
    client_payments_bill_id_client_bills = relationship(
        "ClientBills",
        foreign_keys=[bill_id], 
        backref=backref("client_payments_bill_id_client_billss", cascade="all, delete-orphan")
    )

    # client_payments.client_id -> clients.client_id
    client_payments_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("client_payments_client_id_clientss", cascade="all, delete-orphan")
    )

    # client_payments.created_by -> users.user_id
    client_payments_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_payments_created_by_userss", cascade="all, delete-orphan")
    )

    # client_payments.updated_by -> users.user_id
    client_payments_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("client_payments_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

