"""email_settings"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, Integer, SmallInteger, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class EmailSettings(BaseModel, TimestampMixin):
    __tablename__ = 'email_settings'

    # id : INTEGER
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # from_email : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    from_email: Mapped[str] = mapped_column(String(150), nullable=False)

    # smtp_host : VARCHAR(100) COLLATE "utf8mb4_unicode_ci"
    smtp_host: Mapped[str] = mapped_column(String(100), nullable=False)

    # smtp_port : SMALLINT
    smtp_port: Mapped[int] = mapped_column(SmallInteger, default='587', nullable=False)

    # smtp_user : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    smtp_user: Mapped[str] = mapped_column(String(150), nullable=False)

    # smtp_password : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    smtp_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # encryption_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    encryption_code: Mapped[str] = mapped_column(CHAR(2), ForeignKey("refm_email_encryption.code", ondelete="RESTRICT"), default='T', nullable=False)

    # auth_required_ind : TINYINT
    auth_required_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # is_default : TINYINT
    is_default: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # status_ind : TINYINT
    status_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # email_settings.chamber_id -> chamber.chamber_id
    email_settings_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("email_settings_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # email_settings.encryption_code -> refm_email_encryption.code
    email_settings_encryption_code_refm_email_encryption = relationship(
        "RefmEmailEncryption",
        foreign_keys=[encryption_code], 
        backref=backref("email_settings_encryption_code_refm_email_encryptions", cascade="all, delete-orphan")
    )

    # email_settings.created_by -> users.user_id
    email_settings_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("email_settings_created_by_userss", cascade="all, delete-orphan")
    )

    # email_settings.updated_by -> users.user_id
    email_settings_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("email_settings_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

