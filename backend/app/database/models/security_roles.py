"""security_roles"""

from sqlalchemy import Boolean, CHAR, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class SecurityRoles(BaseModel, TimestampMixin):
    __tablename__ = 'security_roles'

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # role_name : VARCHAR(80) COLLATE "utf8mb4_unicode_ci"
    role_name: Mapped[str] = mapped_column(String(80), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(Text)

    # system_ind : TINYINT
    system_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # admin_ind : TINYINT
    admin_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

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

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

