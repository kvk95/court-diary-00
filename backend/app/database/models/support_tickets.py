"""support_tickets"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class SupportTickets(BaseModel, TimestampMixin):
    __tablename__ = 'support_tickets'

    # ticket_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    ticket_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # ticket_number : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    ticket_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # subject : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # module_code : CHAR(8) COLLATE "utf8mb4_unicode_ci"
    module_code: Mapped[Optional[str]] = mapped_column(CHAR(8), ForeignKey("refm_modules.code", ondelete="SET NULL"))

    # status_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_ticket_status.code", ondelete="RESTRICT"), default='OPEN', nullable=False)

    # priority_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    priority_code: Mapped[Optional[str]] = mapped_column(CHAR(4), default='MEDI')

    # assigned_to : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    assigned_to: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # reported_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    reported_by: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False)

    # reported_date : TIMESTAMP
    reported_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # assigned_date : TIMESTAMP
    assigned_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # resolved_date : TIMESTAMP
    resolved_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # due_date : DATE
    due_date: Mapped[Optional[date]] = mapped_column(Date)

    # deleted_ind : TINYINT
    deleted_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # support_tickets.chamber_id -> chamber.chamber_id
    support_tickets_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("support_tickets_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # support_tickets.module_code -> refm_modules.code
    support_tickets_module_code_refm_modules = relationship(
        "RefmModules",
        foreign_keys=[module_code], 
        backref=backref("support_tickets_module_code_refm_moduless", cascade="all, delete-orphan")
    )

    # support_tickets.status_code -> refm_ticket_status.code
    support_tickets_status_code_refm_ticket_status = relationship(
        "RefmTicketStatus",
        foreign_keys=[status_code], 
        backref=backref("support_tickets_status_code_refm_ticket_statuss", cascade="all, delete-orphan")
    )

    # support_tickets.assigned_to -> users.user_id
    support_tickets_assigned_to_users = relationship(
        "Users",
        foreign_keys=[assigned_to], 
        backref=backref("support_tickets_assigned_to_userss", cascade="all, delete-orphan")
    )

    # support_tickets.reported_by -> users.user_id
    support_tickets_reported_by_users = relationship(
        "Users",
        foreign_keys=[reported_by], 
        backref=backref("support_tickets_reported_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

