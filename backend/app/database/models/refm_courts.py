"""refm_courts"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer, String, Text
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RefmCourts(BaseModel, TimestampMixin):
    __tablename__ = 'refm_courts'

    # court_id : INTEGER
    court_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # court_name : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    court_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # state_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_states.code", ondelete="RESTRICT"), nullable=False)

    # court_type : VARCHAR(60) COLLATE "utf8mb4_unicode_ci"
    court_type: Mapped[Optional[str]] = mapped_column(String(60))

    # address : TEXT COLLATE "utf8mb4_unicode_ci"
    address: Mapped[Optional[str]] = mapped_column(Text)

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # refm_courts.state_code -> refm_states.code
    refm_courts_state_code_refm_states = relationship(
        "RefmStates",
        foreign_keys=[state_code], 
        backref=backref("refm_courts_state_code_refm_statess", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

