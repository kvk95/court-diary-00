"""refm_email_status"""

from sqlalchemy import CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmEmailStatus(BaseModel):
    __tablename__ = 'refm_email_status'

    # code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)

    # description : VARCHAR(40) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(40), nullable=False)

    # color_code : CHAR(7) COLLATE "utf8mb4_unicode_ci"
    color_code: Mapped[Optional[str]] = mapped_column(CHAR(7), default='#64748b')

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmEmailStatusConstants:
    PENDING = 'P'
    SENT = 'S'
    DELIVERED = 'D'
    OPENED = 'O'
    FAILED = 'F'
    BOUNCED = 'B'
