"""refm_email_templates"""

from sqlalchemy import Boolean, CHAR, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RefmEmailTemplates(BaseModel, TimestampMixin):
    __tablename__ = 'refm_email_templates'

    # code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    code: Mapped[str] = mapped_column(CHAR(4), primary_key=True, nullable=False)

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


class RefmEmailTemplatesConstants:
    TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION = 'LTUA'
    TEMPLATE_FOR_PASSWORD_RESET_REQUESTS = 'LTRP'

class RefmEmailTemplatesEnum(str, PyEnum):
    TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION = RefmEmailTemplatesConstants.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION
    TEMPLATE_FOR_PASSWORD_RESET_REQUESTS = RefmEmailTemplatesConstants.TEMPLATE_FOR_PASSWORD_RESET_REQUESTS
