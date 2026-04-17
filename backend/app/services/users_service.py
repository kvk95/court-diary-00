# app/services/users_service.py

from datetime import date, datetime
from typing import Optional, List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.delete_account_requests import DeleteAccountRequests
from app.database.models.refm_email_templates import RefmEmailTemplatesEnum
from app.database.models.refm_img_upload_for import RefmImgUploadForEnum
from app.database.models.refm_user_deletion_status import RefmUserDeletionStatusConstants
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.users import Users
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.database.repositories.delete_account_requests_repository import DeleteAccountRequestsRepository
from app.database.repositories.profile_images_repository import ProfileImagesRepository
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
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
    UserPasswordIn,
    UserStatusToggle,
    UserProfileOut,
    UserFullThemeOut,
    UserStatsOut,
)
from app.dtos.roles_dto import RoleOut
from app.dtos.role_permissions_dto import RolePermissionModuleOut
from app.services.email_link_service import EmailLinkService
from app.services.image_service import ImageService
from app.utils.security import hash_password
from app.utils.utilities import generate_password
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
        chamber_roles_repo: Optional[ChamberRolesRepository] = None,
        users_repo: Optional[UsersRepository] = None,
        user_chamber_link_repo: Optional[UserChamberLinkRepository] = None,
        user_roles_repo: Optional[UserRolesRepository] = None,
        delete_account_repo: Optional[DeleteAccountRequestsRepository] = None,
        role_permissions_repo: Optional[RolePermissionsRepository] = None,
        profile_images_repo: Optional[ProfileImagesRepository] = None,
        image_service: Optional[ImageService] = None,
        email_link_service: Optional[EmailLinkService] = None,
    ):
        super().__init__(session)
        self.chamber_roles_repo = chamber_roles_repo or ChamberRolesRepository()
        self.users_repo = users_repo or UsersRepository()
        self.user_chamber_link_repo = user_chamber_link_repo or UserChamberLinkRepository()
        self.user_roles_repo = user_roles_repo or UserRolesRepository()
        self.delete_account_repo = delete_account_repo or DeleteAccountRequestsRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()
        self.profile_images_repo = profile_images_repo or ProfileImagesRepository()
        self.image_service = image_service or ImageService(session)
        self.email_link_service = email_link_service or EmailLinkService(session=self.session)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS (Now Just Call Repository Methods - No Query Logic)
    # ─────────────────────────────────────────────────────────────────────────

    async def _set_user_role(self, link_id: str, role_id: int) -> None:
        await self.user_roles_repo.set_user_role(
            session=self.session,
            link_id=link_id,
            role_id=role_id,
            current_user_id=self.user_id,
        )

    async def _check_user_chamber_membership(self, email: str) -> dict:
        stmt = select(Users).where(Users.email == email.lower())
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return {"exists": False}
        
        all_links = await self.user_chamber_link_repo.get_all_active_links_for_user(
            session=self.session,
            user_id=user.user_id,
        )
        
        return {
            "exists": True,
            "user": user,
            "user_id": user.user_id,
            "deleted_ind": user.deleted_ind,
            "active_links": all_links,
            "active_chambers_count": len(all_links),
            "active_chamber_ids": [link.chamber_id for link in all_links],
        }

    async def _reactivate_user(self, user_id: str) -> None:
        await self.users_repo.reactivate_deleted_user(
            session=self.session,
            user_id=user_id,
        )
 
    async def _validate_user_payload(self, payload, *, is_edit: bool = False) -> None:
        errors = []
 
        if not is_edit:
            if err := FieldValidator.validate_email(payload.email):
                errors.append(err)
 
        if not is_edit and not payload.first_name:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="first_name is required",
                )
            )
 
        if not is_edit:
            if err := FieldValidator.validate_password(payload.password):
                errors.append(err)
        elif payload.password:
            if err := FieldValidator.validate_password(payload.password):
                errors.append(err)
 
        if payload.phone:
            if err := FieldValidator.validate_phone(payload.phone):
                errors.append(err)
 
        if payload.role_id:
            role = await self.chamber_roles_repo.get_by_id(
                session=self.session,
                id_values=payload.role_id,
            )
            if not role:
                errors.append(
                    ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message="Role not found",
                    )
                )
 
        if errors:
            aggregate_errors(errors=errors)
 
    async def _handle_role_and_image(self, payload, *, user_id: str, link_id: str) -> None:
        if payload.role_id and link_id:
            await self._set_user_role(link_id, payload.role_id)
 
        await self.image_service.handle_image(
            session=self.session,
            payload=payload,
            entity_id=user_id,
            image_upload_code=RefmImgUploadForEnum.USER,
            description="User profile image",
        )

    def _build_user_dto(self, user_data: dict, chamber_id: str) -> UserOut:
        role: Optional[RoleOut] = None
        if user_data.get("role"):
            role = RoleOut(
                role_id=user_data["role"]["role_id"],
                role_code=user_data["role"]["role_code"],
                role_name=user_data["role"]["role_name"],
                description=user_data["role"]["description"],
                status_ind=user_data["role"]["status_ind"],
                admin_ind=user_data["role"]["admin_ind"],
            )

        profile: Optional[UserProfileOut] = None
        if user_data.get("profile"):
            profile = UserProfileOut(
                theme=UserFullThemeOut(
                    header_color=user_data["profile"].get("header_color") or "0 0% 100%",
                    sidebar_color=user_data["profile"].get("sidebar_color") or "0 0% 100%",
                    primary_color=user_data["profile"].get("primary_color") or "32.4 99% 63%",
                    font_family=user_data["profile"].get("font_family") or "Nunito, sans-serif",
                )
            )

        permissions = [
            RolePermissionModuleOut(
                chamber_module_id=p["chamber_module_id"],
                chamber_id=p["chamber_id"],
                chamber_name=p["chamber_name"],
                module_code=p["module_code"],
                module_name=p["module_name"],
                permission_id=p.get("permission_id"),
                role_id=p["role_id"],
                allow_all_ind=p["allow_all_ind"],
                read_ind=p["read_ind"],
                write_ind=p["write_ind"],
                create_ind=p["create_ind"],
                delete_ind=p["delete_ind"],
                import_ind=p["import_ind"],
                export_ind=p["export_ind"],
            )
            for p in user_data.get("permissions", [])
        ]

        return UserOut(
            user_id=user_data["user_id"],
            full_name=f"{user_data['first_name']} {user_data['last_name'] or ''}".strip(),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            phone=user_data["phone"],
            role=role,
            active_ind=user_data["status_ind"],
            advocate_ind=user_data["advocate_ind"],
            image_id=user_data["image_id"],
            image_data=user_data["image_data"],
            last_login_time=user_data["last_login_time"],
            created_date=user_data["created_date"],
            chamber_name=user_data.get("chamber", {}).get("chamber_name"),
            profile=profile,
            permissions=permissions,
            chamber_id=chamber_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # GET USER STATS
    # ─────────────────────────────────────────────────────────────────────────

    async def get_user_stats(self) -> UserStatsOut:
        stats = await self.users_repo.get_user_stats(
            session=self.session,
            chamber_id=self.chamber_id,
        )
        return UserStatsOut(
            total_users=stats["total_users"],
            active_users=stats["active_users"],
            total_roles=stats["total_roles"],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # GET USER FULL DETAILS
    # ─────────────────────────────────────────────────────────────────────────

    async def get_user_full_details(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        chamber_id: Optional[str] = None,
    ) -> UserOut:
        chamber_id = chamber_id if chamber_id else self.chamber_id
        
        user_data = await self.users_repo.get_user_full_details(
            session=self.session,
            user_id=user_id,
            email=email,
            chamber_id=chamber_id,
        )

        if not user_data:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User not found in this chamber",
            )

        return self._build_user_dto(user_data, chamber_id)

    # ─────────────────────────────────────────────────────────────────────────
    # LIST / PAGED
    # ─────────────────────────────────────────────────────────────────────────

    async def users_get_paged(
        self, page: int, 
        limit: int, 
        role_code: Optional[str] = None,
        search: Optional[str] = None, 
        status_ind: Optional[bool]=None,
    ) -> PagingData[UserOut]:
        users, total_records = await self.users_repo.list_users_paginated(
            session=self.session,
            page=page,
            limit=limit,
            chamber_id=self.chamber_id,
            role_code=role_code,
            search=search,
            status_ind=status_ind,
        )
        
        full_users: List[UserOut] = []
        for user_data in users:
            if user_data.get("role"):
                perm_rows = await self.role_permissions_repo.get_role_permissions(
                    session=self.session,
                    chamber_id=self.chamber_id,
                    user_id=user_data["user_id"]
                )
                user_data["permissions"] = perm_rows
            else:
                user_data["permissions"] = []
            
            full_user = self._build_user_dto(user_data, self.chamber_id)
            full_users.append(full_user)

        builder = PagingBuilder(total_records=total_records, page=page, limit=limit)
        return builder.build(records=full_users)

    # ─────────────────────────────────────────────────────────────────────────
    # GET SINGLE
    # ─────────────────────────────────────────────────────────────────────────

    async def users_get_by_id(self, user_id: str) -> UserOut:
        return await self.get_user_full_details(user_id=user_id)

    async def users_get_by_email(self, email: str) -> UserOut:
        return await self.get_user_full_details(email=email)
 
    # ─────────────────────────────────────────────────────────────────────────
    # ADD
    # ─────────────────────────────────────────────────────────────────────────
 
    async def users_add(self, payload: UserCreate) -> UserOut:
        email: str = payload.email if payload.email else ''
        first_name: str = payload.first_name if payload.first_name else ''
        password: str = generate_password()
        payload.password = password
        
        await self._validate_user_payload(payload, is_edit=False)
        membership = await self._check_user_chamber_membership(email)
 
        if not membership["exists"]:
            user = await self.users_repo.create(
                session=self.session,
                data={
                    "email": email.lower(),
                    "first_name": first_name.strip(),
                    "last_name": (payload.last_name or "").strip() or None,
                    "advocate_ind": payload.advocate_ind,
                    "phone": payload.phone,
                    "password_hash": hash_password(password),
                },
            )
            action_type = "User created"
        else:  
            user = membership["user"]
            active_link = await self.user_chamber_link_repo.get_active_link(
                session=self.session,
                user_id=user.user_id,
                chamber_id=self.chamber_id,
            )
            if active_link:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="User is already a member of this chamber",
                )
            if membership["deleted_ind"]:
                await self._reactivate_user(user.user_id)
            action_type = "User reactivated"
 
        link = await self.user_chamber_link_repo.upsert(
            session=self.session,
            filters={
                UserChamberLink.user_id: user.user_id,
                UserChamberLink.chamber_id: self.chamber_id,
            },
            data={
                "chamber_id": self.chamber_id,
                "user_id": user.user_id,
                "left_date": None,
                "status_ind": True,
                "primary_ind": False,
            },
        )
 
        await self._handle_role_and_image(
            payload,
            user_id=user.user_id,
            link_id=link.link_id,
        )

        link_url = await self.email_link_service.generate_link(
            user_id=user.user_id,
            email=user.email,
            template_code=RefmEmailTemplatesEnum.TEMPLATE_FOR_NEW_USER_ACCOUNT_ACTIVATION,
        )

        # 📝 LOG ACTIVITY (Secure: excludes password payload)
        await self.log_entity_change(
            action=action_type,
            entity_type="user",
            entity_id=user.user_id,
            extra_metadata={
                "email": user.email,
                "role_id": payload.role_id,
                "advocate_ind": payload.advocate_ind,
                "is_reactivation": membership.get("exists", False),
            }
        )
 
        return await self.get_user_full_details(user_id=user.user_id)
 
    # ─────────────────────────────────────────────────────────────────────────
    # EDIT
    # ─────────────────────────────────────────────────────────────────────────
 
    async def users_edit(self, user_id: str, payload: UserEdit) -> UserOut:
        link = await self.user_chamber_link_repo.get_first(
            session=self.session,
            filters={
                UserChamberLink.user_id: user_id,
                UserChamberLink.chamber_id: self.chamber_id,
                UserChamberLink.left_date: None,
            },
        )
 
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="User not found in this chamber",
            )
 
        await self._validate_user_payload(payload, is_edit=True)
 
        update_data: dict = {}
 
        if payload.first_name:
            update_data["first_name"] = payload.first_name.strip()
 
        if payload.last_name:
            update_data["last_name"] = payload.last_name.strip() or None
 
        if payload.phone:
            update_data["phone"] = payload.phone
 
        if payload.password and user_id == self.user_id:
            update_data["password_hash"] = hash_password(payload.password)
 
        if payload.advocate_ind is not None:
            update_data["advocate_ind"] = payload.advocate_ind
 
        if update_data:
            await self.users_repo.update(
                session=self.session,
                id_values=user_id,
                data=update_data,
            )
 
        status_changed = False
        if payload.status_ind is not None and link.status_ind != payload.status_ind:
            await self.user_chamber_link_repo.update(
                session=self.session,
                id_values=link.link_id,
                data={"status_ind": payload.status_ind},
            )
            status_changed = True
 
        await self._handle_role_and_image(
            payload,
            user_id=user_id,
            link_id=link.link_id,
        )

        # 📝 LOG ACTIVITY
        fields_logged = list(update_data.keys())
        if status_changed:
            fields_logged.append("status_ind")

        await self.log_entity_change(
            action="User updated",
            entity_type="user",
            entity_id=user_id,
            payload=payload,
            extra_metadata={"updated_fields": fields_logged}
        )
 
        return await self.get_user_full_details(user_id=user_id)

    async def change_password(self, user_id: str, payload: UserPasswordIn) -> UserOut:
        link = await self.user_chamber_link_repo.get_first(
            session=self.session,
            filters={
                UserChamberLink.user_id: user_id,
                UserChamberLink.chamber_id: self.chamber_id,
                UserChamberLink.left_date: None,
            },
        )

        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User not found in this chamber",
            )

        if payload.password and (err := FieldValidator.validate_password(payload.password)):
            raise err
            
        update_data: dict = {}

        if payload.password:
            update_data["password_hash"] = hash_password(payload.password)

        if update_data:
            await self.users_repo.update(
                session=self.session,
                id_values=user_id,
                data=update_data,
            )

        # 📝 LOG ACTIVITY (Secure: never logs password hash or plain text)
        await self.log_entity_change(
            action="User password changed",
            entity_type="user",
            entity_id=user_id,
            extra_metadata={"changed_by": self.user_id}
        )

        return await self.get_user_full_details(user_id=user_id)

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS TOGGLE
    # ─────────────────────────────────────────────────────────────────────────

    async def users_toggle_status(self, payload: UserStatusToggle) -> UserOut:
        if payload.user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot change your own status.",
            )

        link = await self.user_chamber_link_repo.get_active_link(
            session=self.session,
            user_id=payload.user_id,
            chamber_id=self.chamber_id,
        )
        
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {payload.user_id} not found in this chamber",
            )

        if link.status_ind != payload.status_ind:
            await self.user_chamber_link_repo.update(
                session=self.session,
                id_values=link.link_id,
                data={"status_ind": payload.status_ind},
            )

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="User status toggled",
            entity_type="user",
            entity_id=payload.user_id,
            extra_metadata={"new_status": "active" if payload.status_ind else "inactive"}
        )

        return await self.get_user_full_details(user_id=payload.user_id)

    # ─────────────────────────────────────────────────────────────────────────
    # DELETE REQUEST
    # ─────────────────────────────────────────────────────────────────────────

    async def users_delete(self, user_id: str) -> dict:
        if user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot request deletion of your own account. Contact another administrator.",
            )

        link = await self.user_chamber_link_repo.get_active_link(
            session=self.session,
            user_id=user_id,
            chamber_id=self.chamber_id,
        )
        
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User not found in this chamber",
            )

        user = await self.users_repo.get_by_id(session=self.session, id_values=user_id)
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"User {user_id} not found"
            )

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

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="Deletion request created",
            entity_type="deletion_request",
            entity_id=str(deletion_request.request_id),
            extra_metadata={
                "request_no": request_no,
                "target_user_id": user_id,
                "target_user_email": user.email
            }
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
    # APPROVE DELETION
    # ─────────────────────────────────────────────────────────────────────────

    async def approve_deletion_request(self, request_id: int) -> dict:
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

        await self.users_repo.reactivate_deleted_user(
            session=self.session,
            user_id=user.user_id,
        )

        await self.user_chamber_link_repo.unlink_user_from_chamber(
            session=self.session,
            user_id=user.user_id,
            chamber_id=self.chamber_id,
        )

        await self.delete_account_repo.update(
            session=self.session,
            id_values=request_id,
            data={
                "status_code": RefmUserDeletionStatusConstants.DELETED,
                "updated_by": self.user_id,
            },
        )

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="Deletion request approved",
            entity_type="deletion_request",
            entity_id=str(request_id),
            extra_metadata={
                "request_no": request.request_no,
                "target_user_id": user.user_id,
                "target_user_email": user.email
            }
        )

        return {
            "request_id": request_id,
            "request_no": request.request_no,
            "user_id": user.user_id,
            "user_email": user.email,
            "status": "Deleted",
            "message": "User has been successfully deleted and removed from chamber.",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # REJECT DELETION
    # ─────────────────────────────────────────────────────────────────────────

    async def reject_deletion_request(self, request_id: int, payload: DeletionRejectPayload) -> dict:
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

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="Deletion request rejected",
            entity_type="deletion_request",
            entity_id=str(request_id),
            extra_metadata={
                "request_no": request.request_no,
                "target_user_id": request.user_id,
                "rejection_notes": payload.notes
            }
        )

        return {
            "request_id": request_id,
            "request_no": request.request_no,
            "status": "Rejected",
            "message": "Deletion request has been rejected.",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # GET DELETION REQUESTS
    # ─────────────────────────────────────────────────────────────────────────

    async def get_deletion_requests(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> PagingData[DeletionRequestOut]:
        requests, total = await self.delete_account_repo.get_deletion_requests_paginated(
            session=self.session,
            chamber_id=self.chamber_id,
            page=page,
            limit=limit,
            status=status,
        )

        records = [
            DeletionRequestOut(
                request_id=req["request_id"],
                request_no=req["request_no"],
                user_id=req["user_id"],
                user_email=req["user_email"],
                user_name=req["user_name"],
                request_date=req["request_date"],
                status_code=req["status_code"],
                notes=req["notes"],
                created_by=req["created_by"],
            )
            for req in requests
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=records)

    # ─────────────────────────────────────────────────────────────────────────
    # ADD / REMOVE USER FROM CHAMBER
    # ─────────────────────────────────────────────────────────────────────────

    async def users_add_to_chamber(self, user_id: str) -> dict:
        user = await self.users_repo.get_by_id(
            session=self.session,
            id_values=user_id
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} not found",
            )

        active_link = await self.user_chamber_link_repo.get_active_link(
            session=self.session,
            user_id=user_id,
            chamber_id=self.chamber_id,
        )

        if active_link:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="User is already a member of this chamber",
            )

        stmt = select(UserChamberLink).where(
            UserChamberLink.user_id == user_id,
            UserChamberLink.chamber_id == self.chamber_id,
        )
        result = await self.user_chamber_link_repo.execute(stmt, self.session)
        existing_link = result.scalars().first()

        if existing_link:
            updated = await self.user_chamber_link_repo.update(
                session=self.session,
                id_values=existing_link.link_id,
                data={
                    "left_date": None,
                    "status_ind": True,
                },
            )
        else:
            updated = await self.user_chamber_link_repo.create(
                session=self.session,
                data={
                    "user_id": user_id,
                    "chamber_id": self.chamber_id,
                    "primary_ind": False,
                    "status_ind": True,
                },
            )

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="User added to chamber",
            entity_type="user",
            entity_id=user_id,
            extra_metadata={"user_email": user.email, "chamber_id": self.chamber_id}
        )

        return {
            "user_id": user_id,
            "user_email": user.email,
            "added": True,
            "message": "User has been added to this chamber.",
        }

    async def users_remove_from_chamber(self, user_id: str) -> dict:
        if user_id == self.user_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="You cannot remove yourself from the chamber.",
            )

        link = await self.user_chamber_link_repo.get_active_link(
            session=self.session,
            user_id=user_id,
            chamber_id=self.chamber_id,
        )
        
        if not link:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"User {user_id} is not an active member of this chamber",
            )

        user:Users = await self.users_repo.get_by_id(session=self.session, id_values=user_id)

        await self.user_chamber_link_repo.update(
            session=self.session,
            id_values=link.link_id,
            data={
                "left_date": date.today(),
                "status_ind": False,
            },
        )

        # 📝 LOG ACTIVITY
        await self.log_entity_change(
            action="User removed from chamber",
            entity_type="user",
            entity_id=user_id,
            extra_metadata={"user_email": user.email if user else None, 
                            "chamber_id": self.chamber_id}
        )

        return {
            "user_id": user_id,
            "user_email": user.email if user else None,
            "removed": True,
            "message": "User has been removed from this chamber. Their account is preserved.",
        }