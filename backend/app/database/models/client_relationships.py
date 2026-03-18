"""client_relationships"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class ClientRelationships(BaseModel):
    __tablename__ = 'client_relationships'

    # relationship_id : BIGINT
    relationship_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # client_id_from : BIGINT
    client_id_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # client_id_to : BIGINT
    client_id_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # relationship_type : VARCHAR(50) COLLATE "utf8mb4_unicode_ci"
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # is_active : TINYINT
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # client_relationships.client_id_from -> clients.client_id
    client_relationships_client_id_from_clients = relationship(
        "Clients",
        foreign_keys=[client_id_from], 
        backref=backref("client_relationships_client_id_from_clientss", cascade="all, delete-orphan")
    )

    # client_relationships.client_id_to -> clients.client_id
    client_relationships_client_id_to_clients = relationship(
        "Clients",
        foreign_keys=[client_id_to], 
        backref=backref("client_relationships_client_id_to_clientss", cascade="all, delete-orphan")
    )

    # client_relationships.created_by -> users.user_id
    client_relationships_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("client_relationships_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

