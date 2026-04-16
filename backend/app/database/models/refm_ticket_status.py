"""refm_ticket_status"""

from sqlalchemy import Boolean, CHAR, Integer, String, Text
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmTicketStatus(BaseModel):
    __tablename__ = 'refm_ticket_status'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # name : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(Text)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # color_code : VARCHAR(7) COLLATE "utf8mb4_unicode_ci"
    color_code: Mapped[Optional[str]] = mapped_column(String(7), default='#6B7280')

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmTicketStatusConstants:
    OPEN = 'OPEN'
    ASSIGNED = 'ASGN'
    IN_PROGRESS = 'INPR'
    PENDING = 'PEND'
    RESOLVED = 'RSOL'
    CLOSED = 'CLSD'
    REOPENED = 'REOP'

class RefmTicketStatusEnum(str, PyEnum):
    OPEN = RefmTicketStatusConstants.OPEN
    ASSIGNED = RefmTicketStatusConstants.ASSIGNED
    IN_PROGRESS = RefmTicketStatusConstants.IN_PROGRESS
    PENDING = RefmTicketStatusConstants.PENDING
    RESOLVED = RefmTicketStatusConstants.RESOLVED
    CLOSED = RefmTicketStatusConstants.CLOSED
    REOPENED = RefmTicketStatusConstants.REOPENED
