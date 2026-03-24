from typing import List, Dict, Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.role_permissions import RolePermissions
from app.database.models.chamber_modules import ChamberModules
from app.database.models.user_roles import UserRoles
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.chamber import Chamber
from app.database.models.refm_modules import RefmModules
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

    async def get_role_permissions(
        self,
        session: AsyncSession,
        chamber_id: int,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get one permission row per module for the user.
        """
        stmt = (
            select(
                ChamberModules.chamber_module_id,
                ChamberModules.chamber_id,
                Chamber.chamber_name,
                RefmModules.code.label("module_code"),
                RefmModules.name.label("module_name"),
                RolePermissions.permission_id,
                UserRoles.role_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
            )
            .join(
                Chamber,
                Chamber.chamber_id == ChamberModules.chamber_id
            )
            .join(
                UserChamberLink,
                and_(
                    UserChamberLink.chamber_id == chamber_id,
                    UserChamberLink.user_id == user_id,
                    UserChamberLink.left_date.is_(None),
                    UserChamberLink.status_ind.is_(True),
                )
            )
            .join(
                UserRoles,
                and_(
                    UserRoles.link_id == UserChamberLink.link_id,
                    UserRoles.end_date.is_(None)
                )
            )
            # === THIS IS THE MOST IMPORTANT JOIN ===
            .join(
                RolePermissions,
                and_(
                    RolePermissions.role_id == UserRoles.role_id,
                    RolePermissions.chamber_module_id == ChamberModules.chamber_module_id   # ← Key condition
                )
            )
            .join(
                RefmModules,
                RefmModules.code == ChamberModules.module_code
            )
            .where(
                ChamberModules.chamber_id == chamber_id,
                ChamberModules.is_active.is_(True),
            )
        )

        result = await self.execute(stmt, session=session)
        rows = result.all()

        return [
            {
                "chamber_module_id": row.chamber_module_id,
                "chamber_id": row.chamber_id,
                "chamber_name": row.chamber_name,
                "module_code": row.module_code,
                "module_name": row.module_name,
                "permission_id": row.permission_id,
                "role_id": row.role_id,
                "allow_all_ind": row.allow_all_ind,
                "read_ind": row.read_ind,
                "write_ind": row.write_ind,
                "create_ind": row.create_ind,
                "delete_ind": row.delete_ind,
            }
            for row in rows
        ]
    
    async def get_role_permission_matrix(
        self,
        session: AsyncSession,
        role_id: int,
        chamber_id: int,
        module_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns ALL active modules in the chamber for a given role.
        Shows current permission flags or default False if not set yet.
        Used for Role Management / Permission Editor UI.
        """
        stmt = (
            select(
                ChamberModules.chamber_module_id,
                ChamberModules.chamber_id,
                Chamber.chamber_name,
                RefmModules.code.label("module_code"),
                RefmModules.name.label("module_name"),
                RolePermissions.permission_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
            )
            .join(RefmModules, ChamberModules.module_code == RefmModules.code)
            .join(
                Chamber,
                Chamber.chamber_id == ChamberModules.chamber_id
            )
            .outerjoin(
                RolePermissions,
                and_(
                    RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
                    RolePermissions.role_id == role_id,
                )
            )
            .where(
                ChamberModules.chamber_id == chamber_id,
                ChamberModules.is_active.is_(True),
            )
            .order_by(RefmModules.sort_order.asc(), RefmModules.code.asc())
        )

        if module_name and module_name.strip():
            stmt = stmt.where(RefmModules.name.ilike(f"%{module_name.strip()}%"))

        result = await self.execute(stmt, session=session)
        return [dict(row._mapping) for row in result.all()]

    async def has_permission(
        self,
        session: AsyncSession,
        *,
        role_id: int,
        chamber_id: int, 
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