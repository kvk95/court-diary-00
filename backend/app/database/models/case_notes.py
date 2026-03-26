"""case_notes"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class CaseNotes(BaseModel, TimestampMixin):
    __tablename__ = 'case_notes'

    # note_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    note_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # note_text : TEXT COLLATE "utf8mb4_unicode_ci"
    note_text: Mapped[str] = mapped_column(Text, nullable=False)

    # is_private : TINYINT
    is_private: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # is_deleted : TINYINT
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # case_notes.chamber_id -> chamber.chamber_id
    case_notes_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("case_notes_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # case_notes.case_id -> cases.case_id
    case_notes_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("case_notes_case_id_casess", cascade="all, delete-orphan")
    )

    # case_notes.user_id -> users.user_id
    case_notes_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("case_notes_user_id_userss", cascade="all, delete-orphan")
    )

    # case_notes.deleted_by -> users.user_id
    case_notes_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("case_notes_deleted_by_userss", cascade="all, delete-orphan")
    )

    # case_notes.created_by -> users.user_id
    case_notes_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("case_notes_created_by_userss", cascade="all, delete-orphan")
    )

    # case_notes.updated_by -> users.user_id
    case_notes_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("case_notes_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

