"""role_permissions"""

from sqlalchemy import ForeignKey, BigInteger, Boolean, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RolePermissions(BaseModel, TimestampMixin):
    __tablename__ = 'role_permissions'

    # permission_id : BIGINT
    permission_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="CASCADE"), nullable=False)

    # chamber_module_id : INTEGER
    chamber_module_id: Mapped[int] = mapped_column(Integer, ForeignKey("chamber_modules.chamber_module_id", ondelete="CASCADE"), nullable=False)

    # allow_all_ind : TINYINT
    allow_all_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # read_ind : TINYINT
    read_ind: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # write_ind : TINYINT
    write_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # create_ind : TINYINT
    create_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # delete_ind : TINYINT
    delete_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # import_ind : TINYINT
    import_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # export_ind : TINYINT
    export_ind: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # role_permissions.role_id -> security_roles.role_id
    role_permissions_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[role_id], 
        backref=backref("role_permissions_role_id_security_roless", cascade="all, delete-orphan")
    )

    # role_permissions.chamber_module_id -> chamber_modules.chamber_module_id
    role_permissions_chamber_module_id_chamber_modules = relationship(
        "ChamberModules",
        foreign_keys=[chamber_module_id], 
        backref=backref("role_permissions_chamber_module_id_chamber_moduless", cascade="all, delete-orphan")
    )

    # role_permissions.created_by -> users.user_id
    role_permissions_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("role_permissions_created_by_userss", cascade="all, delete-orphan")
    )

    # role_permissions.updated_by -> users.user_id
    role_permissions_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("role_permissions_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

