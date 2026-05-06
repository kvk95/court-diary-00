"""role_permission_master"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RolePermissionMaster(BaseModel, TimestampMixin):
    __tablename__ = 'role_permission_master'

    # id : INTEGER
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # security_role_id : INTEGER
    security_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_roles.role_id", ondelete="CASCADE"), nullable=False)

    # module_code : CHAR(8) COLLATE "utf8mb4_unicode_ci"
    module_code: Mapped[str] = mapped_column(CHAR(8), ForeignKey("refm_modules.code", ondelete="RESTRICT"), nullable=False)

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

    # import_ind : TINYINT
    import_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # export_ind : TINYINT
    export_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # role_permission_master.security_role_id -> security_roles.role_id
    role_permission_master_security_role_id_security_roles = relationship(
        "SecurityRoles",
        foreign_keys=[security_role_id], 
        backref=backref("role_permission_master_security_role_id_security_roless", cascade="all, delete-orphan")
    )

    # role_permission_master.module_code -> refm_modules.code
    role_permission_master_module_code_refm_modules = relationship(
        "RefmModules",
        foreign_keys=[module_code], 
        backref=backref("role_permission_master_module_code_refm_moduless", cascade="all, delete-orphan")
    )

    # role_permission_master.created_by -> users.user_id
    role_permission_master_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("role_permission_master_created_by_userss", cascade="all, delete-orphan")
    )

    # role_permission_master.updated_by -> users.user_id
    role_permission_master_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("role_permission_master_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

