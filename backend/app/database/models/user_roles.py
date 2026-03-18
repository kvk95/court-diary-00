"""user_roles"""

from sqlalchemy import ForeignKey, BigInteger, Date, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class UserRoles(BaseModel, TimestampMixin):
    __tablename__ = 'user_roles'

    # user_role_id : BIGINT
    user_role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # link_id : BIGINT
    link_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_chamber_link.link_id", ondelete="CASCADE"), nullable=False)

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="CASCADE"), nullable=False)

    # start_date : DATE
    start_date: Mapped[date] = mapped_column(Date, server_default=func.curdate(), nullable=False)

    # end_date : DATE
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_roles.link_id -> user_chamber_link.link_id
    user_roles_link_id_user_chamber_link = relationship(
        "UserChamberLink",
        foreign_keys=[link_id], 
        backref=backref("user_roles_link_id_user_chamber_links", cascade="all, delete-orphan")
    )

    # user_roles.role_id -> security_roles.role_id
    user_roles_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[role_id], 
        backref=backref("user_roles_role_id_security_roless", cascade="all, delete-orphan")
    )

    # user_roles.created_by -> users.user_id
    user_roles_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("user_roles_created_by_userss", cascade="all, delete-orphan")
    )

    # user_roles.updated_by -> users.user_id
    user_roles_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("user_roles_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

