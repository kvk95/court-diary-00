"""refm_client_type"""

from sqlalchemy import Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmClientType(BaseModel):
    __tablename__ = 'refm_client_type'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(60), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmClientTypeConstants:
    INDIVIDUAL = 'CTIN'
    CORPORATE = 'CTCO'
    GOVERNMENT = 'CTGO'
    TRUST = 'CTTR'

class RefmClientTypeEnum(str, PyEnum):
    INDIVIDUAL = RefmClientTypeConstants.INDIVIDUAL
    CORPORATE = RefmClientTypeConstants.CORPORATE
    GOVERNMENT = RefmClientTypeConstants.GOVERNMENT
    TRUST = RefmClientTypeConstants.TRUST
