"""refm_comm_status"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCommStatus(BaseModel):
    __tablename__ = 'refm_comm_status'

    # code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True, nullable=False)

    # description : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(50), nullable=False)

    # color_code : CHAR(7) COLLATE "utf8mb4_unicode_ci"
    color_code: Mapped[Optional[str]] = mapped_column(CHAR(7), default='#64748b')

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------


class RefmCommStatusConstants:
    PENDING = 'PN'
    SENT = 'SN'
    DELIVERED = 'DL'
    READ = 'RD'
    FAILED = 'FD'
