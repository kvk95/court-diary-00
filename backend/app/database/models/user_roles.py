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

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="CASCADE"), nullable=False)

    # start_date : DATE
    start_date: Mapped[date] = mapped_column(Date, server_default=func.curdate(), nullable=False)

    # end_date : DATE
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # user_roles.user_id -> users.user_id
    user_roles_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("user_roles_user_id_userss", cascade="all, delete-orphan")
    )

    # user_roles.role_id -> security_roles.role_id
    user_roles_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[role_id], 
        backref=backref("user_roles_role_id_security_roless", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

