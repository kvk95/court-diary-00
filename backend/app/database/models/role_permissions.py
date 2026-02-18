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

    # module_id : INTEGER
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("refm_modules.module_id", ondelete="CASCADE"), nullable=False)

    # allow_all_ind : TINYINT
    allow_all_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # read_ind : TINYINT
    read_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # write_ind : TINYINT
    write_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # create_ind : TINYINT
    create_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # delete_ind : TINYINT
    delete_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger)

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # role_permissions.role_id -> security_roles.role_id
    role_permissions_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[role_id], 
        backref=backref("role_permissions_role_id_security_roless", cascade="all, delete-orphan")
    )

    # role_permissions.module_id -> refm_modules.module_id
    role_permissions_module_id_refm_modules = relationship(
        "RefmModules",
        foreign_keys=[module_id], 
        backref=backref("role_permissions_module_id_refm_moduless", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

