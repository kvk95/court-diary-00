"""user_invitations"""

from sqlalchemy import ForeignKey, BigInteger, CHAR, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date, datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel

class UserInvitations(BaseModel):
    __tablename__ = 'user_invitations'

    # invitation_id : BIGINT
    invitation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chamber.chamber_id", ondelete="CASCADE"), nullable=False)

    # email : VARCHAR(150) COLLATE "utf8mb4_unicode_ci"
    email: Mapped[str] = mapped_column(String(150), nullable=False)

    # role_id : INTEGER
    role_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="SET NULL"))

    # invited_by : BIGINT
    invited_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # invited_date : TIMESTAMP
    invited_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # expires_date : DATE
    expires_date: Mapped[Optional[date]] = mapped_column(Date)

    # status_code : CHAR(2) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(2), default='PN')

    # message : TEXT COLLATE "utf8mb4_unicode_ci"
    message: Mapped[Optional[str]] = mapped_column(Text)

    # accepted_date : TIMESTAMP
    accepted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # accepted_by : BIGINT
    accepted_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_date : TIMESTAMP
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_invitations.chamber_id -> chamber.chamber_id
    user_invitations_chamber_id_chamber = relationship(
        "Chamber",
        foreign_keys=[chamber_id], 
        backref=backref("user_invitations_chamber_id_chambers", cascade="all, delete-orphan")
    )

    # user_invitations.role_id -> security_roles.role_id
    user_invitations_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[role_id], 
        backref=backref("user_invitations_role_id_security_roless", cascade="all, delete-orphan")
    )

    # user_invitations.invited_by -> users.user_id
    user_invitations_invited_by_users = relationship(
        "Users",
        foreign_keys=[invited_by], 
        backref=backref("user_invitations_invited_by_userss", cascade="all, delete-orphan")
    )

    # user_invitations.accepted_by -> users.user_id
    user_invitations_accepted_by_users = relationship(
        "Users",
        foreign_keys=[accepted_by], 
        backref=backref("user_invitations_accepted_by_userss", cascade="all, delete-orphan")
    )

    # user_invitations.created_by -> users.user_id
    user_invitations_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("user_invitations_created_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

