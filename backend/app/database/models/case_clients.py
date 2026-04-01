"""case_clients"""

from sqlalchemy import ForeignKey, Boolean, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class CaseClients(BaseModel, TimestampMixin):
    __tablename__ = 'case_clients'

    # case_client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_client_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # chamber_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # case_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    case_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)

    # party_role_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    party_role_code: Mapped[str] = mapped_column(CHAR(4), ForeignKey("refm_party_roles.code", ondelete="RESTRICT"), nullable=False)

    # primary_ind : TINYINT
    primary_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # engagement_type_code : CHAR(4) COLLATE "utf8mb4_unicode_ci"
    engagement_type_code: Mapped[Optional[str]] = mapped_column(CHAR(4), ForeignKey("refm_engagement_type.code", ondelete="RESTRICT"))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

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

    # case_clients.party_role_code -> refm_party_roles.code
    case_clients_party_role_code_refm_party_roles = relationship(
        "RefmPartyRoles",
        foreign_keys=[party_role_code], 
        backref=backref("case_clients_party_role_code_refm_party_roless", cascade="all, delete-orphan")
    )

    # case_clients.engagement_type_code -> refm_engagement_type.code
    case_clients_engagement_type_code_refm_engagement_type = relationship(
        "RefmEngagementType",
        foreign_keys=[engagement_type_code], 
        backref=backref("case_clients_engagement_type_code_refm_engagement_types", cascade="all, delete-orphan")
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

