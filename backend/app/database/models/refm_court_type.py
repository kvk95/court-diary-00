"""refm_court_type"""

from sqlalchemy import String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCourtType(BaseModel):
    __tablename__ = 'refm_court_type'

    # court_code : VARCHAR(4) COLLATE "utf8mb4_unicode_ci"
    court_code: Mapped[str] = mapped_column(String(4), primary_key=True, nullable=False)

    # description : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(String(50))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

