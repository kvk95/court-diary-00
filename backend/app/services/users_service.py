from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.repositories.role_permissions_repository import (
    RolePermissionsRepository,
)
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.database.repositories.user_roles_repository import UserRolesRepository
from app.database.repositories.users_repository import UsersRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.users_dto import (
    RoleCreate,
    RoleDelete,
    RoleOut,
    RolePermissionEdit,
    RolePermissionOut,
    RoleUpdate,
    UserCreate,
    UserEdit,
    UserOut,
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
        role_permission_repo: Optional[RolePermissionsRepository] = None,
        users_repo: Optional[UsersRepository] = None,
        user_roles_repo: Optional[UserRolesRepository] = None,
    ):
        super().__init__(session)
        self.security_roles_repo:SecurityRolesRepository = security_roles_repo or SecurityRolesRepository()
        self.role_permission_repo:RolePermissionsRepository = role_permission_repo or RolePermissionsRepository()
        self.users_repo:UsersRepository = users_repo or UsersRepository()
        self.user_roles_repo:UserRolesRepository = user_roles_repo or UserRolesRepository()

    # ── Roles ─────────────────────────────────────────────
    async def security_roles_get_paged(
        self,
        page: int,
        limit: int,
        role_name: str | None = None,
        status: bool | None = None,
    ) -> PagingData[RoleOut]:
        conditions = [SecurityRoles.company_id == self.company_id]
        if role_name:
            conditions.append(SecurityRoles.role_name.ilike(f"%{role_name}%"))
        if status is not None:
            conditions.append(SecurityRoles.status_ind == status)

        roles, total = await self.security_roles_repo.list_paginated(
            session=self.session,
            page=page,
            limit=limit,
            where=conditions,
            order_by=[SecurityRoles.role_id.asc()],
        )
        rows = [RoleOut.model_validate(role) for role in roles]
        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=rows)

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        securityRole = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
        )
        return RoleOut.model_validate(securityRole)

    async def security_roles_add(self, payload: RoleCreate) -> RoleOut:
        raw = payload.model_dump(exclude_unset=True, exclude_none=True)
        role_data = self.security_roles_repo.map_fields_to_db_column(raw)

        if not payload.role_name:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR, message="Role name is required"
            )

        existing = await self.security_roles_repo.get_by_name(
            self.session,
            payload.role_name,
            self.company_id,
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role name {payload.role_name} already exists",
            )

        role_data.update({"company_id": self.company_id})
        obj = await self.security_roles_repo.create(
            session=self.session,
            data=role_data,
        )
        return RoleOut.model_validate(obj)

    async def security_roles_update(self, payload: RoleUpdate) -> RoleOut:
        raw = payload.model_dump(exclude_unset=True, exclude_none=True)
        role_data = self.security_roles_repo.map_fields_to_db_column(raw)

        if not payload.role_id:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR, message="Role ID is required"
            )

        existing = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=payload.role_id,
        )
        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role {payload.role_id} not found",
            )

        if payload.role_name:
            duplicate = await self.security_roles_repo.get_by_name(
                self.session,
                payload.role_name,
                self.company_id,
            )
            if duplicate and duplicate.role_id != payload.role_id:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name {payload.role_name} already exists",
                )

        obj = await self.security_roles_repo.update(
            session=self.session,
            id_values=payload.role_id,
            data=role_data,
        )
        return RoleOut.model_validate(obj)

    async def security_roles_delete(self, payload: RoleDelete) -> bool:
        """
        Delete a security role by composite key (role_id + company_id).
        Uses strict CRUD semantics with id_values.
        """
        await self.security_roles_repo.delete(
            session=self.session,
            filters={
                self.security_roles_repo.model.role_id: payload.role_id,
                self.security_roles_repo.model.company_id: self.company_id,
            },
            soft=True,
        )
        return True

    # ── Role Permissions ─────────────────────────────────────────────
    async def role_permissions_get_all(
        self, role_id: int, module_name: str | None = None
    ) -> list[RolePermissionOut]:
        rows = await self.role_permission_repo.get_permissions_for_role(
            self.session,
            role_id,
            self.company_id,
            module_name,
        )
        return [RolePermissionOut.model_validate(row) for row in rows]

    async def role_permissions_edit(
        self, role_id: int, payload: list[RolePermissionEdit]
    ) -> bool:
        for dto in payload:
            raw = dto.model_dump(exclude_unset=True, exclude_none=True)
            item = self.role_permission_repo.map_fields_to_db_column(raw)

            company_module_id = item.get("company_module_id")
            if not company_module_id:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="Company Module ID is required",
                )

            data = {**item, "role_id": role_id, "company_module_id": company_module_id}
            record = await self.role_permission_repo.upsert(
                session=self.session,
                filters={
                    self.role_permission_repo.model.role_id: role_id,
                    self.role_permission_repo.model.company_module_id: company_module_id,
                },
                data=data,
            )
        return True

    # ── Users ─────────────────────────────────────────────
    async def users_get_paged(
        self, page: int, limit: int, search: str | None
    ) -> PagingData[UserOut]:
        users, total_records = await self.users_repo.list_users_paginated(
            session=self.session,
            page=page,
            limit=limit,
            company_id=self.company_id,
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
                "company_id": self.company_id,
                "password_hash": hash_password(userCreate.password),
            }
        )

        user = await self.users_repo.create(
            session=self.session,
            data=data,
        )

        await self.user_roles_repo.create(
            session=self.session,
            data={
                "user_id": user.user_id,
                "role_id": userCreate.role_id,
                "start_date": datetime.now(),
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
            # First remove existing role assignments
            await self.user_roles_repo.delete(
                session=self.session,
                filters={self.user_roles_repo.model.user_id: user_id},
                soft=True,
            )
            # Then assign the new role
            await self.user_roles_repo.create(
                session=self.session,
                data={
                    "user_id": user_id,
                    "role_id": payload.role_id,
                    "start_date": datetime.now(),
                },
            )

        return True
