"""refm_currency"""

from sqlalchemy import Boolean, CHAR, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCurrency(BaseModel):
    __tablename__ = 'refm_currency'

    # code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(3), primary_key=True, nullable=False)

    # description : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(20), nullable=False)

    # symbol : VARCHAR(5) COLLATE "utf8mb4_unicode_ci"
    symbol: Mapped[Optional[str]] = mapped_column(String(5))

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmCurrencyConstants:
    INDIAN_RUPEE = 'INR'
    US_DOLLAR = 'USD'

class RefmCurrencyEnum(str, PyEnum):
    INDIAN_RUPEE = RefmCurrencyConstants.INDIAN_RUPEE
    US_DOLLAR = RefmCurrencyConstants.US_DOLLAR
