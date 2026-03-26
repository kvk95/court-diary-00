# app\database\models\base\timestampmixin.py

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class TimestampMixin:
    # created_date column with default and server_default
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=func.now(),
        nullable=True,
    )

    # updated_date column with default, server_default, and onupdate
    updated_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
