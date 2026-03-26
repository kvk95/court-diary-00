"""chamber_modules"""

from sqlalchemy import ForeignKey, Boolean, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ChamberModules(BaseModel, TimestampMixin):
    __tablename__ = 'chamber_modules'

    # chamber_module_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_module_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # module_code : CHAR(8) COLLATE "utf8mb4_unicode_ci"
    module_code: Mapped[str] = mapped_column(CHAR(8), ForeignKey("refm_modules.code", ondelete="RESTRICT"), nullable=False)

    # is_active : TINYINT
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # chamber_modules.chamber_id -> chamber.chamber_id
    chamber_modules_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("chamber_modules_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # chamber_modules.module_code -> refm_modules.code
    chamber_modules_module_code_refm_modules = relationship(
        "RefmModules",
        foreign_keys=[module_code], 
        backref=backref("chamber_modules_module_code_refm_moduless", cascade="all, delete-orphan")
    )

    # chamber_modules.created_by -> users.user_id
    chamber_modules_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("chamber_modules_created_by_userss", cascade="all, delete-orphan")
    )

    # chamber_modules.updated_by -> users.user_id
    chamber_modules_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("chamber_modules_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

