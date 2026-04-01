"""refm_party_roles"""

from sqlalchemy import Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmPartyRoles(BaseModel):
    __tablename__ = 'refm_party_roles'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(60), nullable=False)

    # category : VARCHAR(30) COLLATE "utf8mb4_unicode_ci"
    category: Mapped[Optional[str]] = mapped_column(String(30))

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmPartyRolesConstants:
    PETITIONER = 'PRPE'
    RESPONDENT = 'PRRE'
    APPELLANT = 'PRAP'
    DEFENDANT = 'PRDE'
    PLAINTIFF = 'PRPL'
    WITNESS = 'PRWI'
    ADVOCATE_ON_RECORD = 'PRAO'

class RefmPartyRolesEnum(str, PyEnum):
    PETITIONER = RefmPartyRolesConstants.PETITIONER
    RESPONDENT = RefmPartyRolesConstants.RESPONDENT
    APPELLANT = RefmPartyRolesConstants.APPELLANT
    DEFENDANT = RefmPartyRolesConstants.DEFENDANT
    PLAINTIFF = RefmPartyRolesConstants.PLAINTIFF
    WITNESS = RefmPartyRolesConstants.WITNESS
    ADVOCATE_ON_RECORD = RefmPartyRolesConstants.ADVOCATE_ON_RECORD
