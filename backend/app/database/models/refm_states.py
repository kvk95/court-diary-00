"""refm_states"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmStates(BaseModel):
    __tablename__ = 'refm_states'

    # state_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)

    # description : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(100), nullable=False)

    # country_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    country_code: Mapped[str] = mapped_column(CHAR(2), ForeignKey("refm_countries.country_code"), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # refm_states.country_code -> refm_countries.country_code
    refm_states_country_code_refm_countries = relationship(
        "RefmCountries",
        foreign_keys=[country_code], 
        backref=backref("refm_states_country_code_refm_countriess", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

