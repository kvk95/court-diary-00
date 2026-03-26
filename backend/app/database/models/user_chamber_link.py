"""user_chamber_link"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class UserChamberLink(BaseModel, TimestampMixin):
    __tablename__ = 'user_chamber_link'

    # link_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    link_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # is_primary : TINYINT
    is_primary: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # joined_date : DATE
    joined_date: Mapped[date] = mapped_column(Date, server_default=func.curdate(), nullable=False)

    # left_date : DATE
    left_date: Mapped[Optional[date]] = mapped_column(Date)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_chamber_link.user_id -> users.user_id
    user_chamber_link_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("user_chamber_link_user_id_userss", cascade="all, delete-orphan")
    )

    # user_chamber_link.chamber_id -> chamber.chamber_id
    user_chamber_link_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("user_chamber_link_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # user_chamber_link.created_by -> users.user_id
    user_chamber_link_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("user_chamber_link_created_by_userss", cascade="all, delete-orphan")
    )

    # user_chamber_link.updated_by -> users.user_id
    user_chamber_link_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("user_chamber_link_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

