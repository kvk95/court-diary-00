from typing import List, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.role_permissions import RolePermissions
from app.database.models.chamber_modules import ChamberModules
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class RolePermissionsRepository(BaseRepository[RolePermissions]):
    """
    Repository for RolePermissions model.
    Handles permission queries scoped to chamber context.
    """

    def __init__(self):
        super().__init__(RolePermissions)

    async def get_permissions_for_login(
        self,
        session: AsyncSession,
        *,
        role_id: int,
        chamber_id: int,
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(
                RolePermissions.permission_id,
                RolePermissions.role_id,
                ChamberModules.module_code,
                ChamberModules.chamber_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
            )
            .join(
                ChamberModules,
                RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
            )
            .where(
                and_(
                    RolePermissions.role_id == role_id,
                    ChamberModules.chamber_id == chamber_id,
                    # ...
                )
            )
        )

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        rows = result.all()

        permissions = []
        for row in rows:
            permissions.append({
                "permission_id": row.permission_id,
                "role_id": row.role_id,
                "module_code": row.module_code,
                "chamber_id": row.chamber_id,
                "allow_all": row.allow_all_ind,
                "read": row.read_ind,
                "write": row.write_ind,
                "create": row.create_ind,
                "delete": row.delete_ind,
            })

        return permissions

    async def has_permission(
        self,
        session: AsyncSession,
        *,
        role_id: int,
        chamber_id: int,  # ✅ Changed from company_id
        module_code: str,
        action: str = "read",  # read, write, create, delete
    ) -> bool:
        """
        Check if a role has a specific permission in a chamber.
        """
        stmt = (
            select(RolePermissions)
            .join(
                ChamberModules,
                RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
            )
            .where(
                and_(
                    RolePermissions.role_id == role_id,
                    ChamberModules.chamber_id == chamber_id,
                    ChamberModules.module_code == module_code,
                    ChamberModules.is_active == True,
                    RolePermissions.is_deleted.is_(False),
                )
            )
        )

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        perm = result.scalars().first()

        if not perm:
            return False

        # Check specific action
        if action == "read":
            return perm.allow_all_ind or perm.read_ind
        elif action == "write":
            return perm.allow_all_ind or perm.write_ind
        elif action == "create":
            return perm.allow_all_ind or perm.create_ind
        elif action == "delete":
            return perm.allow_all_ind or perm.delete_ind

        return False

    async def get_permissions_by_role_and_chamber(
        self,
        session: AsyncSession,
        role_id: int,
        chamber_id: int,
    ) -> List[RolePermissions]:
        """
        Get raw RolePermissions objects for a role in a chamber.
        """
        stmt = (
            select(RolePermissions)
            .join(
                ChamberModules,
                RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
            )
            .where(
                and_(
                    RolePermissions.role_id == role_id,
                    ChamberModules.chamber_id == chamber_id,
                    ChamberModules.is_active == True,
                )
            )
        )

        self._log_stmt(stmt, session)
        result = await session.execute(stmt)
        return list(result.scalars().all())