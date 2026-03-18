"""security_roles"""

from sqlalchemy import BigInteger, Boolean, CHAR, DateTime, Integer, String, Text
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

    # role_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    role_code: Mapped[str] = mapped_column(CHAR(4), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(Text)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : BIGINT
    deleted_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

