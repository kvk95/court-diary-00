"""chamber_roles"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ChamberRoles(BaseModel, TimestampMixin):
    __tablename__ = 'chamber_roles'

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    # security_role_id : INTEGER
    security_role_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="SET NULL"))

    # role_code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    role_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # role_name : VARCHAR(80) COLLATE "utf8mb4_unicode_ci"
    role_name: Mapped[str] = mapped_column(String(80), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(Text)

    # system_ind : TINYINT
    system_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # admin_ind : TINYINT
    admin_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    # chamber_roles.security_role_id -> security_roles.role_id
    chamber_roles_security_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[security_role_id], 
        backref=backref("chamber_roles_security_role_id_security_roless", cascade="all, delete-orphan")
    )

    # chamber_roles.deleted_by -> users.user_id
    chamber_roles_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("chamber_roles_deleted_by_userss", cascade="all, delete-orphan")
    )

    # chamber_roles.created_by -> users.user_id
    chamber_roles_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("chamber_roles_created_by_userss", cascade="all, delete-orphan")
    )

    # chamber_roles.updated_by -> users.user_id
    chamber_roles_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("chamber_roles_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

