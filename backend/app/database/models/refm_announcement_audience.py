"""refm_announcement_audience"""

from sqlalchemy import Boolean, String
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmAnnouncementAudience(BaseModel):
    __tablename__ = 'refm_announcement_audience'

    # code : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False)

    # description : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(String(50))

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmAnnouncementAudienceConstants:
    ALL_CHAMBERS = 'ALL'
    FREE_ONLY = 'FREE'
    PRO_ONLY = 'PRO'

class RefmAnnouncementAudienceEnum(str, PyEnum):
    ALL_CHAMBERS = RefmAnnouncementAudienceConstants.ALL_CHAMBERS
    FREE_ONLY = RefmAnnouncementAudienceConstants.FREE_ONLY
    PRO_ONLY = RefmAnnouncementAudienceConstants.PRO_ONLY
