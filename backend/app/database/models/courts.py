"""courts"""

from sqlalchemy import ForeignKey, CHAR, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class Courts(BaseModel):
    __tablename__ = 'courts'

    # court_code : VARCHAR(12) COLLATE "utf8mb4_unicode_ci"
    court_code: Mapped[str] = mapped_column(String(12), primary_key=True, nullable=False)

    # court_name : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    court_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # state_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    state_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_states.code", ondelete="RESTRICT"))

    # court_type_code : VARCHAR(4) COLLATE "utf8mb4_unicode_ci"
    court_type_code: Mapped[str] = mapped_column(String(4), ForeignKey("refm_court_type.court_code"), nullable=False)

    # parent_court_code : VARCHAR(12) COLLATE "utf8mb4_unicode_ci"
    parent_court_code: Mapped[Optional[str]] = mapped_column(String(12), ForeignKey("courts.court_code"))

    # created_at : TIMESTAMP
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # courts.state_code -> refm_states.code
    courts_state_code_refm_states = relationship(
        "RefmStates",
        foreign_keys=[state_code], 
        backref=backref("courts_state_code_refm_statess", cascade="all, delete-orphan")
    )

    # courts.court_type_code -> refm_court_type.court_code
    courts_court_type_code_refm_court_type = relationship(
        "RefmCourtType",
        foreign_keys=[court_type_code], 
        backref=backref("courts_court_type_code_refm_court_types", cascade="all, delete-orphan")
    )

    # courts.parent_court_code -> courts.court_code
    courts_parent_court_code_courts = relationship(
        "Courts",
        foreign_keys=[parent_court_code], remote_side=[court_code], 
        backref=backref("courts_parent_court_code_courtss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

