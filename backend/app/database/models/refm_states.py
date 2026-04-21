"""refm_states"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmStates(BaseModel):
    __tablename__ = 'refm_states'

    # code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)

    # description : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(100), nullable=False)

    # country_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country_code: Mapped[str] = mapped_column(CHAR(2), ForeignKey("refm_countries.code", ondelete="RESTRICT"), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # refm_states.country_code -> refm_countries.code
    refm_states_country_code_refm_countries = relationship(
        "RefmCountries",
        foreign_keys=[country_code], 
        backref=backref("refm_states_country_code_refm_countriess", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmStatesConstants:
    ANDHRA_PRADESH = 'AP'
    TAMIL_NADU = 'TN'
    ARUNACHAL_PRADESH = 'AR'
    KERALA = 'KL'
    ASSAM = 'AS'
    KARNATAKA = 'KA'
    BIHAR = 'BR'
    MAHARASHTRA = 'MH'
    CHHATTISGARH = 'CG'
    DELHI = 'DL'
    GOA = 'GA'
    GUJARAT = 'GJ'
    HARYANA = 'HR'
    HIMACHAL_PRADESH = 'HP'
    JHARKHAND = 'JH'
    MADHYA_PRADESH = 'MP'
    MANIPUR = 'MN'
    MEGHALAYA = 'ML'
    MIZORAM = 'MZ'
    NAGALAND = 'NL'
    ODISHA = 'OD'
    PUNJAB = 'PB'
    RAJASTHAN = 'RJ'
    SIKKIM = 'SK'
    TELANGANA = 'TS'
    TRIPURA = 'TR'
    UTTAR_PRADESH = 'UP'
    UTTARAKHAND = 'UK'
    WEST_BENGAL = 'WB'
    ANDAMAN_NICOBAR_ISLANDS = 'AN'
    CHANDIGARH = 'CH'
    DADRA_NAGAR_HAVELI_AND_DAMAN_DIU = 'DN'
    JAMMU_KASHMIR = 'JK'
    LADAKH = 'LA'
    LAKSHADWEEP = 'LD'
    PUDUCHERRY = 'PY'

class RefmStatesEnum(str, PyEnum):
    ANDHRA_PRADESH = RefmStatesConstants.ANDHRA_PRADESH
    TAMIL_NADU = RefmStatesConstants.TAMIL_NADU
    ARUNACHAL_PRADESH = RefmStatesConstants.ARUNACHAL_PRADESH
    KERALA = RefmStatesConstants.KERALA
    ASSAM = RefmStatesConstants.ASSAM
    KARNATAKA = RefmStatesConstants.KARNATAKA
    BIHAR = RefmStatesConstants.BIHAR
    MAHARASHTRA = RefmStatesConstants.MAHARASHTRA
    CHHATTISGARH = RefmStatesConstants.CHHATTISGARH
    DELHI = RefmStatesConstants.DELHI
    GOA = RefmStatesConstants.GOA
    GUJARAT = RefmStatesConstants.GUJARAT
    HARYANA = RefmStatesConstants.HARYANA
    HIMACHAL_PRADESH = RefmStatesConstants.HIMACHAL_PRADESH
    JHARKHAND = RefmStatesConstants.JHARKHAND
    MADHYA_PRADESH = RefmStatesConstants.MADHYA_PRADESH
    MANIPUR = RefmStatesConstants.MANIPUR
    MEGHALAYA = RefmStatesConstants.MEGHALAYA
    MIZORAM = RefmStatesConstants.MIZORAM
    NAGALAND = RefmStatesConstants.NAGALAND
    ODISHA = RefmStatesConstants.ODISHA
    PUNJAB = RefmStatesConstants.PUNJAB
    RAJASTHAN = RefmStatesConstants.RAJASTHAN
    SIKKIM = RefmStatesConstants.SIKKIM
    TELANGANA = RefmStatesConstants.TELANGANA
    TRIPURA = RefmStatesConstants.TRIPURA
    UTTAR_PRADESH = RefmStatesConstants.UTTAR_PRADESH
    UTTARAKHAND = RefmStatesConstants.UTTARAKHAND
    WEST_BENGAL = RefmStatesConstants.WEST_BENGAL
    ANDAMAN_NICOBAR_ISLANDS = RefmStatesConstants.ANDAMAN_NICOBAR_ISLANDS
    CHANDIGARH = RefmStatesConstants.CHANDIGARH
    DADRA_NAGAR_HAVELI_AND_DAMAN_DIU = RefmStatesConstants.DADRA_NAGAR_HAVELI_AND_DAMAN_DIU
    JAMMU_KASHMIR = RefmStatesConstants.JAMMU_KASHMIR
    LADAKH = RefmStatesConstants.LADAKH
    LAKSHADWEEP = RefmStatesConstants.LAKSHADWEEP
    PUDUCHERRY = RefmStatesConstants.PUDUCHERRY
