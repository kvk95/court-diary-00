"""refm_hearing_purpose"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmHearingPurpose(BaseModel):
    __tablename__ = 'refm_hearing_purpose'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(60), nullable=False)

    # color_code : CHAR(7) COLLATE "utf8mb4_unicode_ci"
    color_code: Mapped[Optional[str]] = mapped_column(CHAR(7), default='#64748b')

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmHearingPurposeConstants:
    ADMISSION = 'HPAD'
    APPEARANCE = 'HPAP'
    ARGUMENTS = 'HPAR'
    BAIL_HEARING = 'HPBH'
    COMPLIANCE = 'HPCO'
    CROSS_EXAMINATION = 'HPCE'
    EVIDENCE = 'HPEV'
    FRAMING_OF_CHARGES = 'HPFC'
    FRAMING_OF_ISSUES = 'HPFI'
    INTERIM_RELIEF = 'HPIR'
    MEDIATION = 'HPME'
    MENTION = 'HPMN'
    ORDER_PRONOUNCED = 'HPOP'
    PART_HEARD = 'HPPH'
    PLEADINGS = 'HPPL'
    SENTENCING = 'HPSE'
    STEPS = 'HPST'
    SUMMONS_NOTICE = 'HPSN'
    WRITTEN_STATEMENT = 'HPWS'
    OTHER = 'HPOT'
