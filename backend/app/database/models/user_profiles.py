"""user_profiles"""

from sqlalchemy import ForeignKey, BigInteger, CHAR, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class UserProfiles(BaseModel):
    __tablename__ = 'user_profiles'

    # profile_id : BIGINT
    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # address : TEXT COLLATE "utf8mb4_unicode_ci"
    address: Mapped[Optional[str]] = mapped_column(Text)

    # country : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country: Mapped[Optional[str]] = mapped_column(CHAR(2))

    # state : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    state: Mapped[Optional[str]] = mapped_column(CHAR(4))

    # city : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    city: Mapped[Optional[str]] = mapped_column(String(50))

    # postal_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))

    # header_color : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    header_color: Mapped[Optional[str]] = mapped_column(String(20), default='0 0% 100%')

    # sidebar_color : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    sidebar_color: Mapped[Optional[str]] = mapped_column(String(20), default='0 0% 100%')

    # primary_color : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    primary_color: Mapped[Optional[str]] = mapped_column(String(20), default='32.4 99% 63%')

    # font_family : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    font_family: Mapped[Optional[str]] = mapped_column(String(50), default='Nunito, sans-serif')

    # updated_date : TIMESTAMP
    updated_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_profiles.user_id -> users.user_id
    user_profiles_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("user_profiles_user_id_userss", cascade="all, delete-orphan")
    )

    # user_profiles.updated_by -> users.user_id
    user_profiles_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("user_profiles_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

