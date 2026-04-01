"""refm_countries"""

from sqlalchemy import Boolean, CHAR, Integer, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCountries(BaseModel):
    __tablename__ = 'refm_countries'

    # code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)

    # description : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(100), nullable=False)

    # phone_code : VARCHAR(8) COLLATE "utf8mb4_unicode_ci"
    phone_code: Mapped[Optional[str]] = mapped_column(String(8))

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmCountriesConstants:
    INDIA = 'IN'

class RefmCountriesEnum(str, PyEnum):
    INDIA = RefmCountriesConstants.INDIA
