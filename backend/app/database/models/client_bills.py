"""client_bills"""

from sqlalchemy import ForeignKey, BigInteger, CHAR, Date, Numeric, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ClientBills(BaseModel, TimestampMixin):
    __tablename__ = 'client_bills'

    # bill_id : BIGINT
    bill_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : BIGINT
    case_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("cases.case_id", ondelete="SET NULL"))

    # client_id : BIGINT
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

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

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), default='PN')

    # service_description : TEXT COLLATE "utf8mb4_unicode_ci"
    service_description: Mapped[Optional[str]] = mapped_column(Text)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

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

