from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.delete_account_requests import DeleteAccountRequests
from app.database.models.refm_user_deletion_status import RefmUserDeletionStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.repositories.delete_account_requests_repository import DeleteAccountRequestsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.user_roles_repository import UserRolesRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.users_dto import UserCreate, UserEdit, UserOut
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
        user_roles_repo: Optional[UserRolesRepository] = None,
        delete_account_repo: Optional[DeleteAccountRequestsRepository] = None,
    ):
        super().__init__(session)
        self.security_roles_repo = security_roles_repo or SecurityRolesRepository()
        self.users_repo = users_repo or UsersRepository()
        self.user_roles_repo = user_roles_repo or UserRolesRepository()
        self.delete_account_repo = delete_account_repo or DeleteAccountRequestsRepository()

    # ── Users ─────────────────────────────────────────────
    async def users_get_paged(
        self, page: int, limit: int, search: str | None
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

    async def users_add(self, userCreate: UserCreate) -> int:
        raw = userCreate.model_dump(exclude_unset=True, exclude_none=True)
        data = self.users_repo.map_fields_to_db_column(raw)

        errors = []

        if err := FieldValidator.validate_email(userCreate.email):
            errors.append(err)

        if err := FieldValidator.validate_password(userCreate.password):
            errors.append(err)

        if err := FieldValidator.validate_phone(userCreate.phone):
            errors.append(err)

        if userCreate.role_id:
            role = await self.security_roles_repo.get_by_id(
                session=self.session,
                id_values=userCreate.role_id,
            )
            if not role:
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR, message="Role not found"
                    )
                )

        if await self.users_repo.exists_by_email(self.session, data["email"]):
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Email {data['email']} already exists",
                )
            )

        if errors:
            aggregate_errors(errors=errors)

        data.update(
            {
                "password_hash": hash_password(userCreate.password),
            }
        )

        user = await self.users_repo.create(
            session=self.session,
            data=data,
        )

        # Create user_chamber_link for this user
        user_chamber_link = await self.session.execute(
            select(UserChamberLink).where(
                and_(
                    UserChamberLink.user_id == user.user_id,
                    UserChamberLink.chamber_id == self.chamber_id,
                    UserChamberLink.left_date == None,
                )
            )
        )
        link_result = user_chamber_link.scalars().first()
        
        if not link_result:
            from sqlalchemy import insert
            link_stmt = insert(UserChamberLink).values(
                user_id=user.user_id,
                chamber_id=self.chamber_id,
                is_primary=True,
                created_by=self.user_id,
            )
            await self.session.execute(link_stmt)
            await self.session.flush()
            
            link_result = await self.session.execute(
                select(UserChamberLink).where(
                    and_(
                        UserChamberLink.user_id == user.user_id,
                        UserChamberLink.chamber_id == self.chamber_id,
                    )
                )
            )
            link_result = link_result.scalars().first()

        # Assign role via link_id
        if userCreate.role_id and link_result:
            await self.user_roles_repo.create(
                session=self.session,
                data={
                    "link_id": link_result.link_id,
                    "role_id": userCreate.role_id,
                    "start_date": datetime.now(),
                    "created_by": self.user_id,
                },
            )

        return user.user_id

    async def users_edit(self, user_id: int, payload: UserEdit) -> bool:
        user = await self.users_repo.get_by_id(
            session=self.session,
            id_values=user_id,
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR, message="User not found"
            )

        raw = payload.model_dump(exclude_unset=True, exclude_none=True)
        user_fields_in_payload = {k for k in raw.keys() if k != "role_id"}

        if user_fields_in_payload:
            user_data = self.users_repo.map_fields_to_db_column(raw)
            if payload.password:
                user_data["password_hash"] = hash_password(payload.password)

            if payload.email:
                existing = await self.users_repo.get_first(
                    session=self.session,
                    filters={self.users_repo.model.email: payload.email},
                )
                if existing and existing.user_id != user_id:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Email {payload.email} already exists",
                    )

            user = await self.users_repo.update(
                session=self.session,
                id_values=user_id,
                data=user_data,
            )

        # Handle role assignment separately
        if payload.role_id is not None:
            link_result = await self.session.execute(
                select(UserChamberLink).where(
                    and_(
                        UserChamberLink.user_id == user_id,
                        UserChamberLink.chamber_id == self.chamber_id,
                        UserChamberLink.left_date == None,
                    )
                )
            )
            link = link_result.scalars().first()
            
            if link:
                await self.user_roles_repo.delete(
                    session=self.session,
                    filters={
                        self.user_roles_repo.model.link_id: link.link_id,
                    },
                    soft=True,
                )
                await self.user_roles_repo.create(
                    session=self.session,
                    data={
                        "link_id": link.link_id,
                        "role_id": payload.role_id,
                        "start_date": datetime.now(),
                        "created_by": self.user_id,
                    },
                )

        return True

    async def users_delete(self, user_id: int) -> dict:
        """
        Request user deletion (creates delete_account_requests record).
        Does NOT immediately delete the user.
        Returns the request details for tracking.        
        """
        # 1. Verify user exists
        user = await self.users_repo.get_by_id(
            session=self.session,
            id_values=user_id,
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} not found"
            )

        # 2. Check if user is trying to delete themselves
        if user.user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot delete your own account. Please contact another administrator."
            )

        # 3. Check if there's already a pending deletion request
        existing_request = await self.delete_account_repo.get_first(
            session=self.session,
            filters={
                DeleteAccountRequests.user_id: user_id,
                DeleteAccountRequests.status_code: RefmUserDeletionStatusConstants.PENDING
            },
        )
        if existing_request:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Deletion request already exists (Request No: {existing_request.request_no})"
            )

        # 4. Generate unique request number
        request_no = f"DEL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        # 5. Create deletion request
        deletion_request = await self.delete_account_repo.create(
            session=self.session,
            data={
                "chamber_id": self.chamber_id,
                "request_no": request_no,
                "user_id": user_id,
                "request_date": datetime.now(),
                "status_code": RefmUserDeletionStatusConstants.PENDING,  # Pending approval
                "notes": f"Deletion requested by user {self.user_id}",
                "created_by": self.user_id,
            },
        )

        return {
            "request_id": deletion_request.request_id,
            "request_no": request_no,
            "user_id": user_id,
            "user_email": user.email,
            "status": "Pending",
            "message": "Deletion request created successfully. User will be deleted after approval.",
        }

    async def approve_deletion_request(self, request_id: int) -> dict:
        """
        Approve a deletion request and soft-delete the user.
        This should be called by an administrator.
        """
        # 1. Get the deletion request
        request = await self.delete_account_repo.get_by_id(
            session=self.session,
            id_values=request_id,
        )
        if not request:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Deletion request {request_id} not found"
            )

        # 2. Check if request is still pending
        if request.status_code != RefmUserDeletionStatusConstants.PENDING:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Request status is '{request.status_code}', cannot approve"
            )

        # 3. Get the user
        user = await self.users_repo.get_by_id(
            session=self.session,
            id_values=request.user_id,
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {request.user_id} not found"
            )

        # 4. Soft-delete the user
        await self.users_repo.update(
            session=self.session,
            id_values=user.user_id,
            data={
                "is_deleted": True,
                "deleted_date": datetime.now(),
                "deleted_by": self.user_id,
            },
        )

        # 5. Update the deletion request status
        await self.delete_account_repo.update(
            session=self.session,
            id_values=request_id,
            data={
                "status_code": RefmUserDeletionStatusConstants.DELETED,  # Deleted
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

    async def reject_deletion_request(self, request_id: int, notes: str ) -> dict:
        """
        Reject a deletion request.
        """
        # 1. Get the deletion request
        request = await self.delete_account_repo.get_by_id(
            session=self.session,
            id_values=request_id,
        )
        if not request:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Deletion request {request_id} not found"
            )

        # 2. Check if request is still pending
        if request.status_code != RefmUserDeletionStatusConstants.PENDING:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Request status is '{request.status_code}', cannot reject"
            )

        # 3. Update the deletion request status
        await self.delete_account_repo.update(
            session=self.session,
            id_values=request_id,
            data={
                "status_code": RefmUserDeletionStatusConstants.REJECTED,
                "notes": notes or request.notes,
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
        status: str = RefmUserDeletionStatusConstants.PENDING,
    ) -> PagingData[dict]:
        """
        Get all deletion requests (for admin review).
        """
        from sqlalchemy import func

        # Build query
        stmt = select(
            DeleteAccountRequests,
            Users.email,
            Users.first_name,
            Users.last_name,
        ).join(
            Users, DeleteAccountRequests.user_id == Users.user_id
        ).where(
            DeleteAccountRequests.chamber_id == self.chamber_id
        )

        # Filter by status if provided
        if status:
            stmt = stmt.where(DeleteAccountRequests.status_code == status)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        # Apply pagination
        stmt = stmt.order_by(DeleteAccountRequests.request_date.desc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        # Build response
        requests = []
        for req, email, first_name, last_name in rows:
            requests.append({
                "request_id": req.request_id,
                "request_no": req.request_no,
                "user_id": req.user_id,
                "user_email": email,
                "user_name": f"{first_name} {last_name}".strip(),
                "request_date": req.request_date,
                "status_code": req.status_code,
                "notes": req.notes,
                "created_by": req.created_by,
            })

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=requests)