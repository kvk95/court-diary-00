from typing import Optional, List, Dict, Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refm_modules import RefmModules
from app.database.models.chamber_modules import ChamberModules
from app.database.models.role_permissions import RolePermissions
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context

@apply_repo_context
class RolePermissionsRepository(BaseRepository[RolePermissions]):
    """
    Repository for RolePermissions model.
    Provides helpers to fetch permissions for roles and login contexts.
    """

    def __init__(self):
        super().__init__(RolePermissions)

    async def get_permissions_for_role(
        self,
        session: AsyncSession,
        role_id: int,
        company_id: int,
        module_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return permissions for a given role, joined with Modules.
        Optionally filter by module_name (case-insensitive substring).
        """
        stmt = (
            select(
                ChamberModules.chamber_module_id.label("chamber_module_id"),
                RefmModules.name.label("module_name"),
                RefmModules.description.label("description"),
                ChamberModules.is_active.label("is_active"),
                func.coalesce(RolePermissions.allow_all_ind, False).label(
                    "allow_all_ind"
                ),
                func.coalesce(RolePermissions.read_ind, False).label("read_ind"),
                func.coalesce(RolePermissions.write_ind, False).label("write_ind"),
                func.coalesce(RolePermissions.create_ind, False).label("create_ind"),
                func.coalesce(RolePermissions.delete_ind, False).label("delete_ind"),
                func.coalesce(RolePermissions.import_ind, False).label("import_ind"),
                func.coalesce(RolePermissions.export_ind, False).label("export_ind"),
            )
            .join(
                ChamberModules,
                (ChamberModules.module_code == RefmModules.code)
                & (ChamberModules.company_id == company_id)
                & (ChamberModules.is_active.is_(True)),  # Only active allocations
            )
            .outerjoin(
                RolePermissions,
                (RolePermissions.company_module_id == ChamberModules.company_module_id)
                & (RolePermissions.role_id == role_id),
            )
            .order_by(RefmModules.name.asc())
        )

        if module_name:
            stmt = stmt.where(RefmModules.name.ilike(f"%{module_name}%"))

        result = await session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_permissions_for_login(
        self,
        session: AsyncSession,
        role_id: int,
        company_id: int,
        module_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return permissions for login context (slimmer fields).
        Optionally filter by module_name (case-insensitive substring).
        """
        stmt = (
            select(
                RefmModules.code.label("module_code"),
                RefmModules.name.label("module_name"),
                ChamberModules.is_active.label("is_active"),
                func.coalesce(RolePermissions.allow_all_ind, False).label(
                    "allow_all_ind"
                ),
                func.coalesce(RolePermissions.read_ind, False).label("read_ind"),
                func.coalesce(RolePermissions.write_ind, False).label("write_ind"),
                func.coalesce(RolePermissions.create_ind, False).label("create_ind"),
                func.coalesce(RolePermissions.delete_ind, False).label("delete_ind"),
                func.coalesce(RolePermissions.import_ind, False).label("import_ind"),
                func.coalesce(RolePermissions.export_ind, False).label("export_ind"),
            )
            .join(
                ChamberModules,
                (ChamberModules.module_code == RefmModules.code)
                & (ChamberModules.company_id == company_id)
                & (ChamberModules.is_active.is_(True)),  # Only active allocations
            )
            .outerjoin(
                RolePermissions,
                (RolePermissions.company_module_id == ChamberModules.company_module_id)
                & (RolePermissions.role_id == role_id),
            )
            .order_by(RefmModules.name.asc())
        )

        if module_name:
            stmt = stmt.where(RefmModules.name.ilike(f"%{module_name}%"))

        result = await session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
