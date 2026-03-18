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

    # email : VARCHAR(120) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[str] = mapped_column(String(120), nullable=False)

    # password_hash : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # first_name : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)

    # last_name : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    last_name: Mapped[Optional[str]] = mapped_column(String(60))

    # phone : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    # role_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    role_code: Mapped[Optional[str]] = mapped_column(CHAR(4), default='MEMB')

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # email_verified_ind : TINYINT
    email_verified_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # phone_verified_ind : TINYINT
    phone_verified_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # two_factor_ind : TINYINT
    two_factor_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # google_auth_ind : TINYINT
    google_auth_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # last_login_date : TIMESTAMP
    last_login_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # password_changed_date : TIMESTAMP
    password_changed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # users.created_by -> users.user_id
    users_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], remote_side=[user_id], 
        backref=backref("users_created_by_userss", cascade="all, delete-orphan")
    )

    # users.updated_by -> users.user_id
    users_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], remote_side=[user_id], 
        backref=backref("users_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

