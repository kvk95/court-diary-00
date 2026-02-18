"""refm_case_types"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCaseTypes(BaseModel):
    __tablename__ = 'refm_case_types'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(100), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmCaseTypesConstants:
    CRIMINAL = 'CRIM'
    CIVIL_SUIT = 'CIVL'
    WRIT_PETITION = 'WRIT'
    FAMILY_MATTER = 'FAM'
    LABOUR_CASE = 'LAB'
    TAX_MATTER = 'TAX'
    CONSUMER_CASE = 'CON'
