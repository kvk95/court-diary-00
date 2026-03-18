from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_modules import ChamberModules
from app.database.models.role_permissions import RolePermissions
from app.database.models.security_roles import SecurityRoles
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.dtos.role_permissions_dto import (
    RolePermissionEdit,
    RolePermissionMatrixOut,
    RolePermissionModuleOut,
)
from app.validators import ErrorCodes, ValidationErrorDetail

from .base.secured_base_service import BaseSecuredService


class RolePermissionsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        role_permissions_repo: Optional[RolePermissionsRepository] = None,
    ):
        super().__init__(session)
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()

    async def get_permission_matrix(
        self,
        role_id: int,
        module_name: str | None = None,
    ) -> list[RolePermissionModuleOut]:
        """
        Get permission matrix for a role (all modules with permissions).
        This is for SS 2 - showing the toggle matrix.
        """
        # Get all active modules for this chamber
        stmt = (
            select(
                ChamberModules,
                RolePermissions,
            )
            .outerjoin(
                RolePermissions,
                and_(
                    ChamberModules.chamber_module_id == RolePermissions.chamber_module_id,
                    RolePermissions.role_id == role_id,
                ),
            )
            .where(
                ChamberModules.chamber_id == self.chamber_id,
                ChamberModules.is_active == True,
            )
            .order_by(ChamberModules.module_code.asc())
        )

        if module_name:
            stmt = stmt.where(ChamberModules.module_code.ilike(f"%{module_name}%"))

        result = await self.session.execute(stmt)
        rows = result.all()

        # Build response
        permissions = []
        for chamber_module, role_perm in rows:
            permissions.append(RolePermissionModuleOut(
                chamber_module_id=chamber_module.chamber_module_id,
                module_code=chamber_module.module_code,
                module_name=chamber_module.module_code,  # You can join refm_modules for name
                permission_id=role_perm.permission_id if role_perm else None,
                allow_all_ind=role_perm.allow_all_ind if role_perm else False,
                read_ind=role_perm.read_ind if role_perm else False,
                write_ind=role_perm.write_ind if role_perm else False,
                create_ind=role_perm.create_ind if role_perm else False,
                delete_ind=role_perm.delete_ind if role_perm else False,
                # Add import/export if you have those columns
                # import_ind=role_perm.import_ind if role_perm else False,
                # export_ind=role_perm.export_ind if role_perm else False,
            ))

        return permissions

    async def role_permissions_edit(
        self,
        role_id: int,
        payload: list[RolePermissionEdit],
    ) -> bool:
        """
        Update permissions for a role (bulk update from matrix).
        """
        # Verify role exists
        role_stmt = select(SecurityRoles).where(
            SecurityRoles.role_id == role_id,
            SecurityRoles.is_deleted.is_(False),
        )
        role_result = await self.session.execute(role_stmt)
        role = role_result.scalars().first()

        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Role {role_id} not found"
            )

        # Process each permission update
        for dto in payload:
            # Verify chamber_module exists and belongs to this chamber
            module_stmt = select(ChamberModules).where(
                and_(
                    ChamberModules.chamber_module_id == dto.chamber_module_id,
                    ChamberModules.chamber_id == self.chamber_id,
                )
            )
            module_result = await self.session.execute(module_stmt)
            module = module_result.scalars().first()

            if not module:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Module {dto.chamber_module_id} not found in your chamber"
                )

            # Prepare permission data
            perm_data = {
                "role_id": role_id,
                "chamber_module_id": dto.chamber_module_id,
                "allow_all_ind": dto.allow_all_ind,
                "read_ind": dto.read_ind,
                "write_ind": dto.write_ind,
                "create_ind": dto.create_ind,
                "delete_ind": dto.delete_ind,
                # Add import/export if you have those columns
                # "import_ind": dto.import_ind,
                # "export_ind": dto.export_ind,
            }

            # Upsert permission
            await self.role_permissions_repo.upsert(
                session=self.session,
                filters={
                    RolePermissions.role_id: role_id,
                    RolePermissions.chamber_module_id: dto.chamber_module_id,
                },
                data=perm_data,
            )

        return True

    async def get_role_permissions_summary(
        self,
        role_id: int,
    ) -> RolePermissionMatrixOut:
        """
        Get complete permission matrix for a role with role info.
        """
        # Get role info
        role = await self.session.execute(
            select(SecurityRoles).where(SecurityRoles.role_id == role_id)
        )
        role_result = role.scalars().first()

        if not role_result:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Role {role_id} not found"
            )

        # Get permissions
        permissions = await self.get_permission_matrix(role_id)

        return RolePermissionMatrixOut(
            role_id=role_id,
            role_name=role_result.role_name,
            role_code=role_result.role_code,
            permissions=permissions,
        )