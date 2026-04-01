"""refm_proof_type"""

from sqlalchemy import Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmProofType(BaseModel):
    __tablename__ = 'refm_proof_type'

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


class RefmProofTypeConstants:
    AADHAR = 'PTAD'
    PAN = 'PTPN'
    DRIVING_LICENCE = 'PTDL'
    VOTER_ID = 'PTVC'
    COMPANY_REGISTRATION = 'PTCR'
    GST = 'PTGT'

class RefmProofTypeEnum(str, PyEnum):
    AADHAR = RefmProofTypeConstants.AADHAR
    PAN = RefmProofTypeConstants.PAN
    DRIVING_LICENCE = RefmProofTypeConstants.DRIVING_LICENCE
    VOTER_ID = RefmProofTypeConstants.VOTER_ID
    COMPANY_REGISTRATION = RefmProofTypeConstants.COMPANY_REGISTRATION
    GST = RefmProofTypeConstants.GST
