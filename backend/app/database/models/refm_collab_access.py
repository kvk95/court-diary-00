"""refm_collab_access"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class RefmCollabAccess(BaseModel):
    __tablename__ = 'refm_collab_access'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

    # description : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[str] = mapped_column(String(50), nullable=False)

    # permissions : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    permissions: Mapped[Optional[str]] = mapped_column(String(255))

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


class RefmCollabAccessConstants:
    READ_ONLY = 'CARO'
    READ_WRITE = 'CARW'
    FULL_ACCESS = 'CAFU'
