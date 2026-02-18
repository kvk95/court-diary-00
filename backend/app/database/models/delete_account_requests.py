"""delete_account_requests"""

from sqlalchemy import ForeignKey, BigInteger, CHAR, Date, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from datetime import date
from typing import Any, Optional

from app.database.models.base.base_model import BaseModel
from app.database.models.base.timestampmixin import TimestampMixin

class DeleteAccountRequests(BaseModel, TimestampMixin):
    __tablename__ = 'delete_account_requests'

    # request_id : INTEGER
    request_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # chamber_id : BIGINT
    chamber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chambers.chamber_id", ondelete="CASCADE"), nullable=False)

    # request_no : VARCHAR(30) COLLATE "utf8mb4_unicode_ci"
    request_no: Mapped[str] = mapped_column(String(30), nullable=False)

    # user_id : BIGINT
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # request_date : DATE
    request_date: Mapped[date] = mapped_column(Date, nullable=False)

    # status_code : CHAR(1) COLLATE "utf8mb4_unicode_ci"
    status_code: Mapped[Optional[str]] = mapped_column(CHAR(1), ForeignKey("refm_user_deletion_status.code", ondelete="RESTRICT"), default='P')

    # notes : TEXT COLLATE "utf8mb4_unicode_ci"
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # created_by : BIGINT
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # updated_by : BIGINT
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="SET NULL"))

    # FORWARD RELATIONSHIPS ------------------------------------------------------------
    # A forward relationship is defined in the table that contains the foreign key.

    # delete_account_requests.chamber_id -> chambers.chamber_id
    delete_account_requests_chamber_id_chambers = relationship(
        "Chambers",
        foreign_keys=[chamber_id], 
        backref=backref("delete_account_requests_chamber_id_chamberss", cascade="all, delete-orphan")
    )

    # delete_account_requests.user_id -> users.user_id
    delete_account_requests_user_id_users = relationship(
        "Users",
        foreign_keys=[user_id], 
        backref=backref("delete_account_requests_user_id_userss", cascade="all, delete-orphan")
    )

    # delete_account_requests.status_code -> refm_user_deletion_status.code
    delete_account_requests_status_code_refm_user_deletion_status = relationship(
        "RefmUserDeletionStatus",
        foreign_keys=[status_code], 
        backref=backref("delete_account_requests_status_code_refm_user_deletion_statuss", cascade="all, delete-orphan")
    )

    # delete_account_requests.created_by -> users.user_id
    delete_account_requests_created_by_users = relationship(
        "Users",
        foreign_keys=[created_by], 
        backref=backref("delete_account_requests_created_by_userss", cascade="all, delete-orphan")
    )

    # delete_account_requests.updated_by -> users.user_id
    delete_account_requests_updated_by_users = relationship(
        "Users",
        foreign_keys=[updated_by], 
        backref=backref("delete_account_requests_updated_by_userss", cascade="all, delete-orphan")
    )

    # FORWARD RELATIONSHIPS ------------------------------------------------------------

