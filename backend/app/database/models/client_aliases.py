"""client_aliases"""

from sqlalchemy import ForeignKey, CHAR, DateTime, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ClientAliases(BaseModel):
    __tablename__ = 'client_aliases'

    # alias_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    alias_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # alias_name : VARCHAR(200) COLLATE "utf8mb4_unicode_ci"
    alias_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # alias_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    alias_type: Mapped[Optional[str]] = mapped_column(String(50))

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_aliases.client_id -> clients.client_id
    client_aliases_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("client_aliases_client_id_clientss", cascade="all, delete-orphan")
    )

    # client_aliases.created_by -> users.user_id
    client_aliases_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_aliases_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

