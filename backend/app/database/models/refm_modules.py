"""refm_modules"""

from sqlalchemy import Boolean, CHAR, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmModules(BaseModel):
    __tablename__ = 'refm_modules'

    # code : CHAR(8) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(8), primary_key=True, nullable=False)

    # name : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # description : TEXT COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(Text)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmModulesConstants:
    DASHBOARD = 'DASH'
    CASES = 'CASES'
    HEARINGS = 'HEAR'
    CALENDAR = 'CAL'
    USER_MANAGEMENT = 'USERS'
    REPORTS = 'RPT'
    SETTINGS = 'SET'
