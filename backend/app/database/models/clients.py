"""clients"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Clients(BaseModel, TimestampMixin):
    __tablename__ = 'clients'

    # client_id : BIGINT
    client_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # client_type : CHAR(1) COLLATE "utf8mb4_unicode_ci"
    client_type: Mapped[str] = mapped_column(CHAR(1), nullable=False)

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

    # id_proof_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    id_proof_type: Mapped[Optional[str]] = mapped_column(String(50))

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

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # clients.chamber_id -> chamber.chamber_id
    clients_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("clients_chamber_id_chambers", cascade="all, delete-orphan")
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

