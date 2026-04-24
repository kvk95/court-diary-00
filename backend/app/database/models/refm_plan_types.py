"""refm_plan_types"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer, Numeric, String
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship, backref
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

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # email_ind : TINYINT
    email_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # sms_ind : TINYINT
    sms_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # whatsapp_ind : TINYINT
    whatsapp_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # max_users : INTEGER
    max_users: Mapped[Optional[int]] = mapped_column(Integer)

    # max_cases : INTEGER
    max_cases: Mapped[Optional[int]] = mapped_column(Integer)

    # price_monthly_amt : DECIMAL(12, 2)
    price_monthly_amt: Mapped[float] = mapped_column(Numeric, default='0.00', nullable=False)

    # price_annual_amt : DECIMAL(12, 2)
    price_annual_amt: Mapped[float] = mapped_column(Numeric, default='0.00', nullable=False)

    # currency_code : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    currency_code: Mapped[str] = mapped_column(CHAR(3), ForeignKey("refm_currency.code", ondelete="RESTRICT"), default='INR', nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # refm_plan_types.currency_code -> refm_currency.code
    refm_plan_types_currency_code_refm_currency = relationship(
        "RefmCurrency",
        foreign_keys=[currency_code], 
        backref=backref("refm_plan_types_currency_code_refm_currencys", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmPlanTypesConstants:
    FREE = 'PTFR'
    PRO = 'PTPR'
    ENTERPRISE = 'PTEN'

class RefmPlanTypesEnum(str, PyEnum):
    FREE = RefmPlanTypesConstants.FREE
    PRO = RefmPlanTypesConstants.PRO
    ENTERPRISE = RefmPlanTypesConstants.ENTERPRISE
