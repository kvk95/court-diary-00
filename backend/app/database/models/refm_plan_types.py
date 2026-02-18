"""refm_plan_types"""

from sqlalchemy import Boolean, CHAR, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmPlanTypes(BaseModel):
    __tablename__ = 'refm_plan_types'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(60), nullable=False)

    # max_users : INTEGER
    max_users: Mapped[Optional[int]] = mapped_column(Integer)

    # max_cases : INTEGER
    max_cases: Mapped[Optional[int]] = mapped_column(Integer)

    # price_monthly_amt : DECIMAL(12, 2)
    price_monthly_amt: Mapped[Optional[float]] = mapped_column(Numeric, default='0.00')

    # price_annual_amt : DECIMAL(12, 2)
    price_annual_amt: Mapped[Optional[float]] = mapped_column(Numeric, default='0.00')

    # currency_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    currency_code: Mapped[Optional[str]] = mapped_column(CHAR(3), default='INR')

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmPlanTypesConstants:
    FREE = 'FREE'
    PRO = 'PRO'
    ENTERPRISE = 'ENT'
