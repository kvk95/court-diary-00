"""case_collaborations"""

from sqlalchemy import ForeignKey, CHAR, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class CaseCollaborations(BaseModel, TimestampMixin):
    __tablename__ = 'case_collaborations'

    # collaboration_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    collaboration_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # owner_chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    owner_chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # collaborator_chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    collaborator_chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # access_level : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    access_level: Mapped[Optional[str]] = mapped_column(CHAR(2), default='RO')

    # invited_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    invited_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # invited_date : TIMESTAMP
    invited_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # accepted_date : TIMESTAMP
    accepted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), default='PN')

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # case_collaborations.case_id -> cases.case_id
    case_collaborations_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("case_collaborations_case_id_casess", cascade="all, delete-orphan")
    )

    # case_collaborations.owner_chamber_id -> chamber.chamber_id
    case_collaborations_owner_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[owner_chamber_id], 
        backref=backref("case_collaborations_owner_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # case_collaborations.collaborator_chamber_id -> chamber.chamber_id
    case_collaborations_collaborator_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[collaborator_chamber_id], 
        backref=backref("case_collaborations_collaborator_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # case_collaborations.invited_by -> users.user_id
    case_collaborations_invited_by_users = relationship(
        "Users",
        foreign_keys=[invited_by], 
        backref=backref("case_collaborations_invited_by_userss", cascade="all, delete-orphan")
    )

    # case_collaborations.created_by -> users.user_id
    case_collaborations_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("case_collaborations_created_by_userss", cascade="all, delete-orphan")
    )

    # case_collaborations.updated_by -> users.user_id
    case_collaborations_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("case_collaborations_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

