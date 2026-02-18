"""email_templates"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Integer, SmallInteger, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class EmailTemplates(BaseModel, TimestampMixin):
    __tablename__ = 'email_templates'

    # id : INTEGER
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id", ondelete="CASCADE"), nullable=False)

    # code : CHAR(30) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(30), ForeignKey("refm_email_templates.code", ondelete="RESTRICT"), nullable=False)

    # subject : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # content : LONGTEXT
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    # is_customized : TINYINT
    is_customized: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # enabled_ind : TINYINT
    enabled_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # version : SMALLINT
    version: Mapped[Optional[int]] = mapped_column(SmallInteger, default='1')

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # email_templates.chamber_id -> chambers.chamber_id
    email_templates_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("email_templates_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # email_templates.code -> refm_email_templates.code
    email_templates_code_refm_email_templates = relationship(
        "RefmEmailTemplates",
        foreign_keys=[code], 
        backref=backref("email_templates_code_refm_email_templatess", cascade="all, delete-orphan")
    )

    # email_templates.created_by -> users.user_id
    email_templates_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("email_templates_created_by_userss", cascade="all, delete-orphan")
    )

    # email_templates.updated_by -> users.user_id
    email_templates_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("email_templates_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

