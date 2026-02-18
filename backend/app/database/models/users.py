"""users"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class Users(BaseModel, TimestampMixin):
    __tablename__ = 'users'

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id"), nullable=False)

    # email : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    # password_hash : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # first_name : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # last_name : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    last_name: Mapped[Optional[str]] = mapped_column(String(50))

    # phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # role_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    role_code: Mapped[Optional[str]] = mapped_column(CHAR(3), default='MEM')

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # email_verified : TINYINT
    email_verified: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # phone_verified : TINYINT
    phone_verified: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # two_factor_enabled : TINYINT
    two_factor_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # google_auth_connected : TINYINT
    google_auth_connected: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # last_login_date : TIMESTAMP
    last_login_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # password_changed_date : TIMESTAMP
    password_changed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # users.chamber_id -> chambers.chamber_id
    users_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("users_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

