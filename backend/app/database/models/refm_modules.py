"""refm_modules"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmModules(BaseModel):
    __tablename__ = 'refm_modules'

    # module_id : INTEGER
    module_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # module_code : CHAR(20) COLLATE "utf8mb4_unicode_ci"
    module_code: Mapped[str] = mapped_column(CHAR(20), nullable=False)

    # module_name : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # sort_order : INTEGER
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

