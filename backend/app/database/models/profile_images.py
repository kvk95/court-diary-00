"""profile_images"""

from sqlalchemy import ForeignKey, Boolean, CHAR, DateTime, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import datetime
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class ProfileImages(BaseModel, TimestampMixin):
    __tablename__ = 'profile_images'

    # image_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    image_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, nullable=False)

    # user_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"))

    # client_id : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    client_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("clients.client_id", ondelete="CASCADE"))

    # image_data : LONGTEXT
    image_data: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    # description : VARCHAR(255) COLLATE "utf8mb4_unicode_ci"
    description: Mapped[Optional[str]] = mapped_column(String(255))

    # deleted_ind : TINYINT
    deleted_ind: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)

    # deleted_date : TIMESTAMP
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # deleted_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    deleted_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # created_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : CHAR(36) COLLATE "utf8mb4_unicode_ci"
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # profile_images.user_id -> users.user_id
    profile_images_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("profile_images_user_id_userss", cascade="all, delete-orphan")
    )

    # profile_images.client_id -> clients.client_id
    profile_images_client_id_clients = relationship(
        "Clients",
        foreign_keys=[client_id], 
        backref=backref("profile_images_client_id_clientss", cascade="all, delete-orphan")
    )

    # profile_images.deleted_by -> users.user_id
    profile_images_deleted_by_users = relationship(
        "Users",
        foreign_keys=[deleted_by], 
        backref=backref("profile_images_deleted_by_userss", cascade="all, delete-orphan")
    )

    # profile_images.created_by -> users.user_id
    profile_images_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("profile_images_created_by_userss", cascade="all, delete-orphan")
    )

    # profile_images.updated_by -> users.user_id
    profile_images_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("profile_images_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

