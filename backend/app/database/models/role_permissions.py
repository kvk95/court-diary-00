"""role_permissions"""

from sqlalchemy import ForeignKey, Boolean, CHAR, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class RolePermissions(BaseModel, TimestampMixin):
    __tablename__ = 'role_permissions'

    # permission_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    permission_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # role_id : INTEGER
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("chamber_roles.role_id", ondelete="CASCADE"), nullable=False)

    # chamber_module_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    chamber_module_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("chamber_modules.chamber_module_id", ondelete="CASCADE"), nullable=False)

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

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # role_permissions.role_id -> chamber_roles.role_id
    role_permissions_role_id_chamber_roles = relationship(
        "ChamberRoles",
        foreign_keys=[role_id], 
        backref=backref("role_permissions_role_id_chamber_roless", cascade="all, delete-orphan")
    )

    # role_permissions.chamber_module_id -> chamber_modules.chamber_module_id
    role_permissions_chamber_module_id_chamber_modules = relationship(
        "ChamberModules",
        foreign_keys=[chamber_module_id], 
        backref=backref("role_permissions_chamber_module_id_chamber_moduless", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

