"""clients"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Clients(BaseModel, TimestampMixin):
    __tablename__ = 'clients'

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # client_type_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    client_type_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_client_type.code", ondelete="RESTRICT"), nullable=False)

    # party_type_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    party_type_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_party_type.code", ondelete="RESTRICT"), nullable=False)

    # client_name : VARCHAR(200) COLLATE "utf8mb4_unicode_ci"
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # display_name : VARCHAR(200) COLLATE "utf8mb4_unicode_ci"
    display_name: Mapped[Optional[str]] = mapped_column(String(200))

    # contact_person : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    contact_person: Mapped[Optional[str]] = mapped_column(String(150))

    # email : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[Optional[str]] = mapped_column(String(150))

    # phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # alternate_phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    alternate_phone: Mapped[Optional[str]] = mapped_column(String(20))

    # address_line1 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))

    # address_line2 : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))

    # city : VARCHAR(80) COLLATE "utf8mb4_unicode_ci"
    city: Mapped[Optional[str]] = mapped_column(String(80))

    # state_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_states.code", ondelete="SET NULL"))

    # postal_code : VARCHAR(12) COLLATE "utf8mb4_unicode_ci"
    postal_code: Mapped[Optional[str]] = mapped_column(String(12))

    # country_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country_code: Mapped[Optional[str]] = mapped_column(CHAR(2), ForeignKey("refm_countries.code", ondelete="RESTRICT"), default='IN')

    # id_proof_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    id_proof_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_proof_type.code", ondelete="RESTRICT"))

    # id_proof_number : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    id_proof_number: Mapped[Optional[str]] = mapped_column(String(100))

    # source_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    source_code: Mapped[Optional[str]] = mapped_column(String(20))

    # referral_source : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    referral_source: Mapped[Optional[str]] = mapped_column(String(150))

    # client_since : DATE
    client_since: Mapped[Optional[date]] = mapped_column(Date)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # clients.chamber_id -> chamber.chamber_id
    clients_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("clients_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # clients.client_type_code -> refm_client_type.code
    clients_client_type_code_refm_client_type = relationship(
        "RefmClientType",
        foreign_keys=[client_type_code], 
        backref=backref("clients_client_type_code_refm_client_types", cascade="all, delete-orphan")
    )

    # clients.party_type_code -> refm_party_type.code
    clients_party_type_code_refm_party_type = relationship(
        "RefmPartyType",
        foreign_keys=[party_type_code], 
        backref=backref("clients_party_type_code_refm_party_types", cascade="all, delete-orphan")
    )

    # clients.state_code -> refm_states.code
    clients_state_code_refm_states = relationship(
        "RefmStates",
        foreign_keys=[state_code], 
        backref=backref("clients_state_code_refm_statess", cascade="all, delete-orphan")
    )

    # clients.country_code -> refm_countries.code
    clients_country_code_refm_countries = relationship(
        "RefmCountries",
        foreign_keys=[country_code], 
        backref=backref("clients_country_code_refm_countriess", cascade="all, delete-orphan")
    )

    # clients.id_proof_code -> refm_proof_type.code
    clients_id_proof_code_refm_proof_type = relationship(
        "RefmProofType",
        foreign_keys=[id_proof_code], 
        backref=backref("clients_id_proof_code_refm_proof_types", cascade="all, delete-orphan")
    )

    # clients.deleted_by -> users.user_id
    clients_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("clients_deleted_by_userss", cascade="all, delete-orphan")
    )

    # clients.created_by -> users.user_id
    clients_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("clients_created_by_userss", cascade="all, delete-orphan")
    )

    # clients.updated_by -> users.user_id
    clients_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("clients_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

