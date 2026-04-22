"""refm_court_type"""

from sqlalchemy import Boolean, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCourtType(BaseModel):
    __tablename__ = 'refm_court_type'

    # code : VARCHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(String(4), primary_key=True, nullable=False)

    # description : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(String(50))

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmCourtTypeConstants:
    CIVIL_COURT = 'CIVI'
    DISTRICT_COURT = 'DIST'
    FAMILY_COURT = 'FAMI'
    HIGH_COURT = 'HIGH'
    MAGISTRATE = 'MAGI'
    SPECIAL_COURT = 'SPEC'
    SUPREME_COURT = 'SUPR'
    TRIBUNAL = 'TRIB'

class RefmCourtTypeEnum(str, PyEnum):
    CIVIL_COURT = RefmCourtTypeConstants.CIVIL_COURT
    DISTRICT_COURT = RefmCourtTypeConstants.DISTRICT_COURT
    FAMILY_COURT = RefmCourtTypeConstants.FAMILY_COURT
    HIGH_COURT = RefmCourtTypeConstants.HIGH_COURT
    MAGISTRATE = RefmCourtTypeConstants.MAGISTRATE
    SPECIAL_COURT = RefmCourtTypeConstants.SPECIAL_COURT
    SUPREME_COURT = RefmCourtTypeConstants.SUPREME_COURT
    TRIBUNAL = RefmCourtTypeConstants.TRIBUNAL
