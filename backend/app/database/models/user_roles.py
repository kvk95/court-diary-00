"""user_roles"""

from sqlalchemy import ForeignKey, CHAR, Date, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class UserRoles(BaseModel, TimestampMixin):
    __tablename__ = 'user_roles'

    # user_role_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_role_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # link_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    link_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("user_chamber_link.link_id", ondelete="CASCADE"), nullable=False)

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("chamber_roles.role_id", ondelete="CASCADE"), nullable=False)

    # start_date : DATE
    start_date: Mapped[date] = mapped_column(Date, server_default=func.curdate(), nullable=False)

    # end_date : DATE
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_roles.link_id -> user_chamber_link.link_id
    user_roles_link_id_user_chamber_link = relationship(
        "UserChamberLink",
        foreign_keys=[link_id], 
        backref=backref("user_roles_link_id_user_chamber_links", cascade="all, delete-orphan")
    )

    # user_roles.role_id -> chamber_roles.role_id
    user_roles_role_id_chamber_roles = relationship(
        "ChamberRoles",
        foreign_keys=[role_id], 
        backref=backref("user_roles_role_id_chamber_roless", cascade="all, delete-orphan")
    )

    # user_roles.created_by -> users.user_id
    user_roles_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("user_roles_created_by_userss", cascade="all, delete-orphan")
    )

    # user_roles.updated_by -> users.user_id
    user_roles_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("user_roles_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

