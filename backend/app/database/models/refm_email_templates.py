"""refm_email_templates"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RefmEmailTemplates(BaseModel, TimestampMixin):
    __tablename__ = 'refm_email_templates'

    # code : CHAR(30) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(30), primary_key=True, nullable=False)

    # subject : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # content : LONGTEXT
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    # category : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    category: Mapped[Optional[str]] = mapped_column(String(50))

    # description : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(String(255))

    # sort_order : INTEGER
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # status_ind : TINYINT
    status_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    #    -- No relationships defined. --

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

