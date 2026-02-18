"""case_notes"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class CaseNotes(BaseModel, TimestampMixin):
    __tablename__ = 'case_notes'

    # note_id : BIGINT
    note_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id"), nullable=False)

    # case_id : BIGINT
    case_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("cases.case_id"), nullable=False)

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    # note_text : TEXT COLLATE "utf8mb4_unicode_ci"
    note_text: Mapped[str] = mapped_column(Text, nullable=False)

    # is_private : TINYINT
    is_private: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # case_notes.chamber_id -> chambers.chamber_id
    case_notes_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("case_notes_chamber_id_chamberss", cascade="all, delete-orphan")
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

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

