"""refm_invoice_status"""

from sqlalchemy import Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmInvoiceStatus(BaseModel):
    __tablename__ = 'refm_invoice_status'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(30) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(30), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmInvoiceStatusConstants:
    PENDING = 'PEND'
    PAID = 'PAID'
    FAILED = 'FAIL'

class RefmInvoiceStatusEnum(str, PyEnum):
    PENDING = RefmInvoiceStatusConstants.PENDING
    PAID = RefmInvoiceStatusConstants.PAID
    FAILED = RefmInvoiceStatusConstants.FAILED
