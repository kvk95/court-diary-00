from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_modules import ChamberModules
from app.database.models.refm_modules import RefmModules
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
        module_name: Optional[str] = None,
    ) -> List[RolePermissionModuleOut]:
        """
        All active chamber modules for this chamber, each annotated with the
        role's current permission flags (or all-False if no row yet).
        Joins refm_modules to get the human-readable module name.
        """
        stmt = (
            select(
                ChamberModules.chamber_module_id,
                ChamberModules.module_code,
                RefmModules.name.label("module_name"),
                RolePermissions.permission_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
            )
            .join(RefmModules, ChamberModules.module_code == RefmModules.code)
            .outerjoin(
                RolePermissions,
                and_(
                    ChamberModules.chamber_module_id == RolePermissions.chamber_module_id,
                    RolePermissions.role_id == role_id,
                ),
            )
            .where(
                ChamberModules.chamber_id == self.chamber_id,
                ChamberModules.is_active.is_(True),
            )
            .order_by(RefmModules.sort_order.asc(), ChamberModules.module_code.asc())
        )

        if module_name and module_name.strip():
            stmt = stmt.where(RefmModules.name.ilike(f"%{module_name.strip()}%"))

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            RolePermissionModuleOut(
                chamber_module_id=row.chamber_module_id,
                module_code=row.module_code,
                module_name=row.module_name or row.module_code,
                permission_id=row.permission_id,
                allow_all_ind=bool(row.allow_all_ind) if row.allow_all_ind is not None else False,
                read_ind=bool(row.read_ind) if row.read_ind is not None else False,
                write_ind=bool(row.write_ind) if row.write_ind is not None else False,
                create_ind=bool(row.create_ind) if row.create_ind is not None else False,
                delete_ind=bool(row.delete_ind) if row.delete_ind is not None else False,
            )
            for row in rows
        ]

    async def role_permissions_edit(
        self,
        role_id: int,
        payload: List[RolePermissionEdit],
    ) -> bool:
        """
        Bulk upsert permissions for a role from the toggle matrix.
        Validates role existence and that each module belongs to this chamber.
        """
        # Verify role exists and is not deleted
        role_result = await self.session.execute(
            select(SecurityRoles).where(
                SecurityRoles.role_id == role_id,
                SecurityRoles.is_deleted.is_(False),
            )
        )
        role = role_result.scalars().first()
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )

        for dto in payload:
            # Verify module belongs to this chamber
            module_result = await self.session.execute(
                select(ChamberModules).where(
                    and_(
                        ChamberModules.chamber_module_id == dto.chamber_module_id,
                        ChamberModules.chamber_id == self.chamber_id,
                        ChamberModules.is_active.is_(True),
                    )
                )
            )
            module = module_result.scalars().first()
            if not module:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Module {dto.chamber_module_id} not found or inactive in your chamber",
                )

            perm_data = {
                "role_id": role_id,
                "chamber_module_id": dto.chamber_module_id,
                "allow_all_ind": dto.allow_all_ind,
                "read_ind": dto.read_ind,
                "write_ind": dto.write_ind,
                "create_ind": dto.create_ind,
                "delete_ind": dto.delete_ind,
            }

            await self.role_permissions_repo.upsert(
                session=self.session,
                filters={
                    RolePermissions.role_id: role_id,
                    RolePermissions.chamber_module_id: dto.chamber_module_id,
                },
                data=perm_data,
            )

        return True

    async def get_role_permissions_summary(self, role_id: int) -> RolePermissionMatrixOut:
        """Full permission matrix + role info (for the detail page)."""
        role_result = await self.session.execute(
            select(SecurityRoles).where(SecurityRoles.role_id == role_id)
        )
        role = role_result.scalars().first()
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )

        permissions = await self.get_permission_matrix(role_id)

        return RolePermissionMatrixOut(
            role_id=role_id,
            role_name=role.role_name,
            role_code=role.role_code,
            permissions=permissions,
        )
