"""refm_announcement_type"""

from sqlalchemy import String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmAnnouncementType(BaseModel):
    __tablename__ = 'refm_announcement_type'

    # code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False)

    # name : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    name: Mapped[Optional[str]] = mapped_column(String(50))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmAnnouncementTypeConstants:
    FEATURE = 'FEAT'
    INFO = 'INFO'
    MAINTENANCE = 'MAINT'
    UPDATE = 'UPDT'

class RefmAnnouncementTypeEnum(str, PyEnum):
    FEATURE = RefmAnnouncementTypeConstants.FEATURE
    INFO = RefmAnnouncementTypeConstants.INFO
    MAINTENANCE = RefmAnnouncementTypeConstants.MAINTENANCE
    UPDATE = RefmAnnouncementTypeConstants.UPDATE
