"""case_clients"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, CHAR, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class CaseClients(BaseModel, TimestampMixin):
    __tablename__ = 'case_clients'

    # case_client_id : BIGINT
    case_client_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : BIGINT
    case_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # client_id : BIGINT
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # party_role : CHAR(3) COLLATE "utf8mb4_unicode_ci"
    party_role: Mapped[str] = mapped_column(CHAR(3), nullable=False)

    # is_primary : TINYINT
    is_primary: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # engagement_type : VARCHAR(20) COLLATE "utf8mb4_unicode_ci"
    engagement_type: Mapped[Optional[str]] = mapped_column(String(20))

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # case_clients.chamber_id -> chamber.chamber_id
    case_clients_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("case_clients_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # case_clients.case_id -> cases.case_id
    case_clients_case_id_cases = relationship(
        "Cases",
        foreign_keys=[case_id], 
        backref=backref("case_clients_case_id_casess", cascade="all, delete-orphan")
    )

    # case_clients.client_id -> clients.client_id
    case_clients_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("case_clients_client_id_clientss", cascade="all, delete-orphan")
    )

    # case_clients.created_by -> users.user_id
    case_clients_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("case_clients_created_by_userss", cascade="all, delete-orphan")
    )

    # case_clients.updated_by -> users.user_id
    case_clients_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("case_clients_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

