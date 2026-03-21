from datetime import date, datetime
from typing import Optional
import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.delete_account_requests import DeleteAccountRequests
from app.database.models.refm_user_deletion_status import RefmUserDeletionStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users
from app.database.repositories.delete_account_requests_repository import DeleteAccountRequestsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.user_chamber_link_repository import UserChamberLinkRepository
from app.database.repositories.user_roles_repository import UserRolesRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.users_dto import (
    DeletionRejectPayload,
    DeletionRequestOut,
    UserCreate,
    UserEdit,
    UserOut,
    UserStatusToggle,
)
from app.utils.security import hash_password
from app.validators import (
    ErrorCodes,
    FieldValidator,
    ValidationErrorDetail,
    aggregate_errors,
)

from .base.secured_base_service import BaseSecuredService


class UsersService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        security_roles_repo: Optional[SecurityRolesRepository] = None,
        users_repo: Optional[UsersRepository] = None,
        user_chamber_link_repo: Optional[UserChamberLinkRepository] = None,
        user_roles_repo: Optional[UserRolesRepository] = None,
        delete_account_repo: Optional[DeleteAccountRequestsRepository] = None,
    ):
        super().__init__(session)
        self.security_roles_repo = security_roles_repo or SecurityRolesRepository()
        self.users_repo = users_repo or UsersRepository()
        self.user_chamber_link_repo = user_chamber_link_repo or UserChamberLinkRepository()
        self.user_roles_repo = user_roles_repo or UserRolesRepository()
        self.delete_account_repo = delete_account_repo or DeleteAccountRequestsRepository()

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    async def _get_active_link(self, user_id: int) -> Optional[UserChamberLink]:
        """Get the active user_chamber_link row for this user in the current chamber."""
        result = await self.session.execute(
            select(UserChamberLink).where(
                and_(
                    UserChamberLink.user_id == user_id,
                    UserChamberLink.chamber_id == self.chamber_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
        )
        return result.scalars().first()

    async def _set_user_role(self, link_id: int, role_id: int) -> None:
        """
        Replace the current active role for a link with a new one.
        Closes any existing open role assignment then creates a new one.
        Uses hard delete on the old row since user_roles has no soft-delete column.
        """
        # End current active role(s) by setting end_date = today
        existing = await self.session.execute(
            select(UserRoles).where(
                and_(
                    UserRoles.link_id == link_id,
                    UserRoles.end_date.is_(None),
                )
            )
        )
        for old_role in existing.scalars().all():
            old_role.end_date = date.today()
        await self.session.flush()

        # Create new assignment
        await self.user_roles_repo.create(
            session=self.session,
            data={
                "link_id": link_id,
                "role_id": role_id,
                "start_date": date.today(),
                "created_by": self.user_id,
            },
        )

    # ─────────────────────────────────────────────────────────────────────────
    # LIST
    # ─────────────────────────────────────────────────────────────────────────

    async def users_get_paged(
        self, page: int, limit: int, search: Optional[str] = None
    ) -> PagingData[UserOut]:
        users, total_records = await self.users_repo.list_users_paginated(
            session=self.session,
            page=page,
            limit=limit,
            chamber_id=self.chamber_id,
            search=search,
        )
        builder = PagingBuilder(total_records=total_records, page=page, limit=limit)
        return builder.build(records=users)

    # ─────────────────────────────────────────────────────────────────────────
    # GET SINGLE
    # ─────────────────────────────────────────────────────────────────────────

    async def users_get_by_id(self, user_id: int) -> UserOut:
        """Fetch a single user by ID, scoped to the current chamber."""
        users, _ = await self.users_repo.list_users_paginated(
            session=self.session,
            page=1,
            limit=1,
            chamber_id=self.chamber_id,
            search=None,
        )
        # Filter by user_id from the paginated result isn't ideal for a single fetch;
        # use a direct query instead.
        row = await self.users_repo.get_user_with_profile_and_role(
            session=self.session,
            user_id=user_id,
            chamber_id=self.chamber_id,
        )
        if not row:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} not found in this chamber",
            )
        user, _, role = row
        return UserOut(
            user_id=user.user_id,
            full_name=f"{user.first_name} {user.last_name or ''}".strip(),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            status_ind=user.status_ind,
            role_id=role.role_id if role else None,
            role_name=role.role_name if role else None,
            created_date=user.created_date,
            image="/assets/images/avatar/none.png",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # ADD
    # ─────────────────────────────────────────────────────────────────────────

    async def users_add(self, payload: UserCreate) -> int:
        errors = []

        if err := FieldValidator.validate_email(payload.email):
            errors.append(err)

        if err := FieldValidator.validate_password(payload.password):
            errors.append(err)

        if payload.phone:
            if err := FieldValidator.validate_phone(payload.phone):
                errors.append(err)

        if payload.role_id:
            role = await self.security_roles_repo.get_by_id(
                session=self.session,
                id_values=payload.role_id,
            )
            if not role:
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR, message="Role not found"
                    )
                )

        # Email is globally unique across all chambers
        if payload.email and await self.users_repo.exists_by_email(
            self.session, payload.email.strip().lower()
        ):
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Email '{payload.email}' is already registered",
                )
            )

        if errors:
            aggregate_errors(errors=errors)

        # Create user
        user = await self.users_repo.create(
            session=self.session,
            data={
                "email": payload.email.strip().lower(),
                "first_name": payload.first_name.strip(),
                "last_name": (payload.last_name or "").strip() or None,
                "phone": payload.phone,
                "password_hash": hash_password(payload.password),
                "status_ind": payload.status_ind,
            },
        )

        # Create user_chamber_link
        link = await self.user_chamber_link_repo.create(
            session=self.session,
            data={
                "user_id": user.user_id,
                "chamber_id": self.chamber_id,
                "is_primary": True,
                "joined_date": date.today(),
                "status_ind": True,
                "created_by": self.user_id,
            },
        )

        # Assign role
        if payload.role_id and link:
            await self._set_user_role(link.link_id, payload.role_id)

        return user.user_id

    # ─────────────────────────────────────────────────────────────────────────
    # EDIT
    # ─────────────────────────────────────────────────────────────────────────

    async def users_edit(self, user_id: int, payload: UserEdit) -> UserOut:
        # Verify user belongs to this chamber
        link = await self._get_active_link(user_id)
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} not found in this chamber",
            )

        update_data: dict = {}
        if payload.first_name is not None:
            update_data["first_name"] = payload.first_name.strip()
        if payload.last_name is not None:
            update_data["last_name"] = payload.last_name.strip() or None
        if payload.phone is not None:
            if payload.phone and (err := FieldValidator.validate_phone(payload.phone)):
                raise err
            update_data["phone"] = payload.phone
        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        if update_data:
            await self.users_repo.update(
                session=self.session,
                id_values=user_id,
                data=update_data,
            )

        # Handle role change
        if payload.role_id is not None:
            role = await self.security_roles_repo.get_by_id(
                session=self.session, id_values=payload.role_id
            )
            if not role:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR, message="Role not found"
                )
            await self._set_user_role(link.link_id, payload.role_id)

        return await self.users_get_by_id(user_id)

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS TOGGLE
    # ─────────────────────────────────────────────────────────────────────────

    async def users_toggle_status(self, payload: UserStatusToggle) -> UserOut:
        """Activate or deactivate a user (cannot act on yourself)."""
        if payload.user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot change your own status.",
            )

        link = await self._get_active_link(payload.user_id)
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {payload.user_id} not found in this chamber",
            )

        await self.users_repo.update(
            session=self.session,
            id_values=payload.user_id,
            data={"status_ind": payload.status_ind},
        )
        return await self.users_get_by_id(payload.user_id)

    # ─────────────────────────────────────────────────────────────────────────
    # DELETE REQUEST
    # ─────────────────────────────────────────────────────────────────────────

    async def users_delete(self, user_id: int) -> dict:
        """Create a deletion request (does NOT immediately delete). Needs admin approval."""
        if user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot request deletion of your own account. Contact another administrator.",
            )

        # Verify user is in this chamber
        link = await self._get_active_link(user_id)
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} not found in this chamber",
            )

        user = await self.users_repo.get_by_id(session=self.session, id_values=user_id)
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"User {user_id} not found"
            )

        # Prevent duplicate pending requests
        existing = await self.delete_account_repo.get_first(
            session=self.session,
            filters={
                DeleteAccountRequests.user_id: user_id,
                DeleteAccountRequests.status_code: RefmUserDeletionStatusConstants.PENDING,
            },
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"A pending deletion request already exists (Request No: {existing.request_no})",
            )

        request_no = f"DEL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        deletion_request = await self.delete_account_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "request_no": request_no,
                "user_id": user_id,
                "request_date": date.today(),
                "status_code": RefmUserDeletionStatusConstants.PENDING,
                "notes": f"Deletion requested by user_id={self.user_id}",
                "created_by": self.user_id,
            },
        )

        return {
            "request_id": deletion_request.request_id,
            "request_no": request_no,
            "user_id": user_id,
            "user_email": user.email,
            "status": "Pending",
            "message": "Deletion request created. User will be removed after admin approval.",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # APPROVE / REJECT DELETION
    # ─────────────────────────────────────────────────────────────────────────

    async def approve_deletion_request(self, request_id: int) -> dict:
        """Approve a pending deletion request and soft-delete the user."""
        request = await self.delete_account_repo.get_by_id(
            session=self.session, id_values=request_id
        )
        if not request or request.chamber_id != self.chamber_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Deletion request {request_id} not found",
            )

        if request.status_code != RefmUserDeletionStatusConstants.PENDING:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Request is already '{request.status_code}', cannot approve",
            )

        user = await self.users_repo.get_by_id(
            session=self.session, id_values=request.user_id
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {request.user_id} not found",
            )

        # Soft-delete user
        await self.users_repo.update(
            session=self.session,
            id_values=user.user_id,
            data={
                "is_deleted": True,
                "deleted_date": datetime.now(),
                "deleted_by": self.user_id,
                "status_ind": False,
            },
        )

        # Mark deletion request as done
        await self.delete_account_repo.update(
            session=self.session,
            id_values=request_id,
            data={
                "status_code": RefmUserDeletionStatusConstants.DELETED,
                "updated_by": self.user_id,
            },
        )

        return {
            "request_id": request_id,
            "request_no": request.request_no,
            "user_id": user.user_id,
            "user_email": user.email,
            "status": "Deleted",
            "message": "User has been successfully deleted.",
        }

    async def reject_deletion_request(self, request_id: int, payload: DeletionRejectPayload) -> dict:
        """Reject a pending deletion request."""
        request = await self.delete_account_repo.get_by_id(
            session=self.session, id_values=request_id
        )
        if not request or request.chamber_id != self.chamber_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Deletion request {request_id} not found",
            )

        if request.status_code != RefmUserDeletionStatusConstants.PENDING:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Request is already '{request.status_code}', cannot reject",
            )

        await self.delete_account_repo.update(
            session=self.session,
            id_values=request_id,
            data={
                "status_code": RefmUserDeletionStatusConstants.REJECTED,
                "notes": payload.notes or request.notes,
                "updated_by": self.user_id,
            },
        )

        return {
            "request_id": request_id,
            "request_no": request.request_no,
            "status": "Rejected",
            "message": "Deletion request has been rejected.",
        }

    async def get_deletion_requests(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> PagingData[DeletionRequestOut]:
        """Get all deletion requests for this chamber (admin view)."""
        from sqlalchemy import func

        stmt = (
            select(
                DeleteAccountRequests,
                Users.email,
                Users.first_name,
                Users.last_name,
            )
            .join(Users, DeleteAccountRequests.user_id == Users.user_id)
            .where(DeleteAccountRequests.chamber_id == self.chamber_id)
        )

        if status:
            stmt = stmt.where(DeleteAccountRequests.status_code == status)

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        stmt = stmt.order_by(DeleteAccountRequests.request_date.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        records = [
            DeletionRequestOut(
                request_id=req.request_id,
                request_no=req.request_no,
                user_id=req.user_id,
                user_email=email,
                user_name=f"{first_name} {last_name or ''}".strip(),
                request_date=req.request_date,
                status_code=req.status_code,
                notes=req.notes,
                created_by=req.created_by,
            )
            for req, email, first_name, last_name in rows
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=records)
