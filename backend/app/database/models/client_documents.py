"""client_documents"""

from sqlalchemy import ForeignKey, CHAR, Date, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ClientDocuments(BaseModel, TimestampMixin):
    __tablename__ = 'client_documents'

    # document_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    document_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="SET NULL"))

    # document_name : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # document_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    document_type: Mapped[Optional[str]] = mapped_column(String(50))

    # document_category : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    document_category: Mapped[Optional[str]] = mapped_column(String(50))

    # received_date : DATE
    received_date: Mapped[Optional[date]] = mapped_column(Date)

    # received_from : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    received_from: Mapped[Optional[str]] = mapped_column(String(150))

    # returned_date : DATE
    returned_date: Mapped[Optional[date]] = mapped_column(Date)

    # returned_to : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    returned_to: Mapped[Optional[str]] = mapped_column(String(150))

    # custody_status : CHAR(1) COLLATE "utf8mb4_unicode_ci"
    custody_status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='H')

    # storage_location : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    storage_location: Mapped[Optional[str]] = mapped_column(String(100))

    # file_number : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    file_number: Mapped[Optional[str]] = mapped_column(String(50))

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_documents.chamber_id -> chamber.chamber_id
    client_documents_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("client_documents_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # client_documents.client_id -> clients.client_id
    client_documents_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("client_documents_client_id_clientss", cascade="all, delete-orphan")
    )

    # client_documents.case_id -> cases.case_id
    client_documents_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("client_documents_case_id_casess", cascade="all, delete-orphan")
    )

    # client_documents.created_by -> users.user_id
    client_documents_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_documents_created_by_userss", cascade="all, delete-orphan")
    )

    # client_documents.updated_by -> users.user_id
    client_documents_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("client_documents_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

