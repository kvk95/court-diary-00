"""contact_messages"""

from sqlalchemy import BigInteger, Boolean, CHAR, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ContactMessages(BaseModel, TimestampMixin):
    __tablename__ = 'contact_messages'

    # message_id : BIGINT
    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # full_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # email : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[str] = mapped_column(String(150), nullable=False)

    # subject : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[Optional[str]] = mapped_column(String(255))

    # message : TEXT COLLATE "utf8mb4_unicode_ci"
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # audit_user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    audit_user_id: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

