# app/services/role_permissions_service.py

from typing import List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_modules import ChamberModules
from app.database.models.role_permissions import RolePermissions
from app.database.models.chamber_roles import ChamberRoles
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.dtos.role_permissions_dto import (
    RolePermissionEdit,
    RolePermissionMatrixOut,
    RolePermissionModuleOut,
    RolePermissionsSummaryOut,
)
from app.validators import ErrorCodes, ValidationErrorDetail

from .base.secured_base_service import BaseSecuredService


class RolePermissionsService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        role_permissions_repo: Optional[RolePermissionsRepository] = None,
        chamber_roles_repo: Optional[ChamberRolesRepository] = None,
    ):
        super().__init__(session)
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()
        self.chamber_roles_repo = chamber_roles_repo or ChamberRolesRepository()

    async def get_permission_matrix(
        self,
        role_id: int,
        module_name: Optional[str] = None,
    ) -> List[RolePermissionModuleOut]:
        """Get permission matrix for a specific role."""
        rows = await self.role_permissions_repo.get_role_permission_matrix(
            session=self.session,
            role_id=role_id,
            chamber_id=self.chamber_id,
            module_name=module_name,
        )

        return [
            RolePermissionModuleOut(
                chamber_module_id=row["chamber_module_id"],
                chamber_id=row["chamber_id"],
                chamber_name=row["chamber_name"],
                module_code=row["module_code"],
                module_name=row["module_name"] or row["module_code"],
                permission_id=row.get("permission_id"),
                role_id=role_id,
                allow_all_ind=bool(row.get("allow_all_ind")) if row.get("allow_all_ind") is not None else False,
                read_ind=bool(row.get("read_ind")) if row.get("read_ind") is not None else False,
                write_ind=bool(row.get("write_ind")) if row.get("write_ind") is not None else False,
                create_ind=bool(row.get("create_ind")) if row.get("create_ind") is not None else False,
                delete_ind=bool(row.get("delete_ind")) if row.get("delete_ind") is not None else False,
                import_ind=bool(row.get("import_ind")) if row.get("import_ind") is not None else False,
                export_ind=bool(row.get("export_ind")) if row.get("export_ind") is not None else False,
            )
            for row in rows
        ]

    # ✅ NEW: Get all roles with permission summary
    async def get_all_roles_permissions_summary(
        self,
    ) -> List[RolePermissionsSummaryOut]:
        """Get summary of all roles with their permission counts."""
        rows = await self.role_permissions_repo.get_all_roles_permissions_summary(
            session=self.session,
            chamber_id=self.chamber_id,
        )

        return [
            RolePermissionsSummaryOut(
                role_id=row["role_id"],
                role_name=row["role_name"],
                description=row["description"],
                status_ind=row["status_ind"],
                total_modules=row["total_modules"],
                modules_with_access=row["modules_with_access"],
            )
            for row in rows
        ]

    # ✅ NEW: Get all roles with full permission matrix
    async def get_all_roles_full_matrix(
        self,
    ) -> dict:
        """
        Get complete permission matrix for ALL roles.
        Returns grouped structure: {roles: [...], modules: [...], permissions: [...]}
        """
        rows = await self.role_permissions_repo.get_all_roles_full_matrix(
            session=self.session,
            chamber_id=self.chamber_id,
        )

        # Group by role
        roles_dict = {}
        modules_dict = {}

        for row in rows:
            # Build roles list
            if row["role_id"] not in roles_dict:
                roles_dict[row["role_id"]] = {
                    "role_id": row["role_id"],
                    "role_name": row["role_name"],
                }

            # Build modules list
            if row["chamber_module_id"] not in modules_dict:
                modules_dict[row["chamber_module_id"]] = {
                    "chamber_module_id": row["chamber_module_id"],
                    "module_code": row["module_code"],
                    "module_name": row["module_name"],
                    "sort_order": row["sort_order"],
                }

        # Build permissions matrix (role_id × module_id)
        permissions = []
        for row in rows:
            permissions.append({
                "role_id": row["role_id"],
                "chamber_module_id": row["chamber_module_id"],
                "permission_id": row.get("permission_id"),
                "allow_all_ind": bool(row.get("allow_all_ind")) if row.get("allow_all_ind") is not None else False,
                "read_ind": bool(row.get("read_ind")) if row.get("read_ind") is not None else False,
                "write_ind": bool(row.get("write_ind")) if row.get("write_ind") is not None else False,
                "create_ind": bool(row.get("create_ind")) if row.get("create_ind") is not None else False,
                "delete_ind": bool(row.get("delete_ind")) if row.get("delete_ind") is not None else False,
                "import_ind": bool(row.get("import_ind")) if row.get("import_ind") is not None else False,  # ✅ NEW
                "export_ind": bool(row.get("export_ind")) if row.get("export_ind") is not None else False,  # ✅ NEW
            })

        return {
            "roles": list(roles_dict.values()),
            "modules": sorted(modules_dict.values(), key=lambda x: x["sort_order"]),
            "permissions": permissions,
        }

    async def role_permissions_edit(
        self,
        role_id: int,
        payload: List[RolePermissionEdit],
    ) -> bool:
        """Bulk upsert permissions for a role from the toggle matrix."""
        # Verify role exists and is not deleted
        role_result = await self.session.execute(
            select(ChamberRoles).where(
                ChamberRoles.role_id == role_id,
                ChamberRoles.is_deleted.is_(False),
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
                "import_ind": dto.import_ind,  # ✅ NEW
                "export_ind": dto.export_ind,  # ✅ NEW
            }

            await self.role_permissions_repo.upsert(
                session=self.session,
                filters={
                    RolePermissions.chamber_role_id: role_id,
                    RolePermissions.chamber_module_id: dto.chamber_module_id,
                },
                data=perm_data,
            )

        return True

    async def get_role_permissions_summary(self, role_id: int) -> RolePermissionMatrixOut:
        """Full permission matrix + role info (for the detail page)."""
        role_result = await self.session.execute(
            select(ChamberRoles).where(ChamberRoles.role_id == role_id)
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
            permissions=permissions,
        )