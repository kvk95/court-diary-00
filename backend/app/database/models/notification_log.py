"""notification_log"""

from sqlalchemy import CHAR, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class NotificationLog(BaseModel):
    __tablename__ = 'notification_log'

    # notification_log_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    notification_log_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), nullable=False)

    # hearing_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    hearing_id: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # channel_code : CHAR(10) COLLATE "utf8mb4_unicode_ci"
    channel_code: Mapped[str] = mapped_column(CHAR(10), nullable=False)

    # type_code : CHAR(10) COLLATE "utf8mb4_unicode_ci"
    type_code: Mapped[str] = mapped_column(CHAR(10), nullable=False)

    # ref_date : DATE
    ref_date: Mapped[Optional[date]] = mapped_column(Date)

    # scheduled_at : TIMESTAMP
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # sent_at : TIMESTAMP
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # status_code : CHAR(10) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(10), default='PENDING')

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

