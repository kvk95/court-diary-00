"""client_communications"""

from sqlalchemy import ForeignKey, BigInteger, CHAR, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ClientCommunications(BaseModel):
    __tablename__ = 'client_communications'

    # comm_id : BIGINT
    comm_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # client_id : BIGINT
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # case_id : BIGINT
    case_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("cases.case_id", ondelete="SET NULL"))

    # user_id : BIGINT
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # comm_type : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    comm_type: Mapped[str] = mapped_column(CHAR(2), nullable=False)

    # subject : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[Optional[str]] = mapped_column(String(255))

    # message_preview : TEXT COLLATE "utf8mb4_unicode_ci"
    message_preview: Mapped[Optional[str]] = mapped_column(Text)

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), default='PN')

    # scheduled_at : DATETIME
    scheduled_at: Mapped[Optional[date]] = mapped_column(Date)

    # sent_at : DATETIME
    sent_at: Mapped[Optional[date]] = mapped_column(Date)

    # delivered_at : DATETIME
    delivered_at: Mapped[Optional[date]] = mapped_column(Date)

    # read_at : DATETIME
    read_at: Mapped[Optional[date]] = mapped_column(Date)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_communications.chamber_id -> chamber.chamber_id
    client_communications_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("client_communications_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # client_communications.client_id -> clients.client_id
    client_communications_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("client_communications_client_id_clientss", cascade="all, delete-orphan")
    )

    # client_communications.case_id -> cases.case_id
    client_communications_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("client_communications_case_id_casess", cascade="all, delete-orphan")
    )

    # client_communications.user_id -> users.user_id
    client_communications_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("client_communications_user_id_userss", cascade="all, delete-orphan")
    )

    # client_communications.created_by -> users.user_id
    client_communications_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_communications_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

