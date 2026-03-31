from typing import List, Dict, Any, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.types import Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.role_permissions import RolePermissions
from app.database.models.chamber_modules import ChamberModules
from app.database.models.user_roles import UserRoles
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.chamber import Chamber
from app.database.models.chamber_roles import ChamberRoles
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
        chamber_id: str,
        user_id: str,
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
                RolePermissions.import_ind,
                RolePermissions.export_ind,
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
            .outerjoin(
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
                ChamberModules.active_ind.is_(True),
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
                "allow_all_ind": bool(row.allow_all_ind) if row.allow_all_ind is not None else False,
                "read_ind": bool(row.read_ind) if row.read_ind is not None else False,
                "write_ind": bool(row.write_ind) if row.write_ind is not None else False,
                "create_ind": bool(row.create_ind) if row.create_ind is not None else False,
                "delete_ind": bool(row.delete_ind) if row.delete_ind is not None else False,
                "import_ind": bool(row.import_ind) if row.import_ind is not None else False,
                "export_ind": bool(row.export_ind) if row.export_ind is not None else False,
            }
            for row in rows
        ]
    
    async def get_role_permission_matrix(
        self,
        session: AsyncSession,
        role_id: int,
        chamber_id: str,
        module_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns ALL active modules in the chamber for a given role.
        Shows current permission flags or default False if no permission row exists yet.
        Used for Role Management / Permission Editor UI (toggle matrix).
        """
        stmt = (
            select(
                ChamberModules.chamber_module_id,
                ChamberModules.chamber_id,
                Chamber.chamber_name,
                RefmModules.code.label("module_code"),
                RefmModules.name.label("module_name"),
                RefmModules.sort_order,
                RolePermissions.permission_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
                RolePermissions.import_ind,
                RolePermissions.export_ind,
            )
            .join(RefmModules, ChamberModules.module_code == RefmModules.code)
            .join(
                Chamber,
                Chamber.chamber_id == ChamberModules.chamber_id
            )
            # Outer join so we get ALL modules even if no permission row exists for this role
            .outerjoin(
                RolePermissions,
                and_(
                    RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
                    RolePermissions.role_id == role_id,        # ← Correct column
                )
            )
            .where(
                ChamberModules.chamber_id == chamber_id,
                ChamberModules.active_ind.is_(True),
            )
            .order_by(RefmModules.sort_order.asc(), RefmModules.code.asc())
        )

        if module_name and module_name.strip():
            stmt = stmt.where(RefmModules.name.ilike(f"%{module_name.strip()}%"))

        result = await self.execute(stmt, session=session)
        rows = result.all()

        return [
            {
                "chamber_module_id": row.chamber_module_id,
                "chamber_id": row.chamber_id,
                "chamber_name": row.chamber_name,
                "module_code": row.module_code,
                "module_name": row.module_name or row.module_code,
                "sort_order": row.sort_order,
                "permission_id": row.permission_id,
                "allow_all_ind": bool(row.allow_all_ind) if row.allow_all_ind is not None else False,
                "read_ind": bool(row.read_ind) if row.read_ind is not None else False,
                "write_ind": bool(row.write_ind) if row.write_ind is not None else False,
                "create_ind": bool(row.create_ind) if row.create_ind is not None else False,
                "delete_ind": bool(row.delete_ind) if row.delete_ind is not None else False,
                "import_ind": bool(row.import_ind) if row.import_ind is not None else False,
                "export_ind": bool(row.export_ind) if row.export_ind is not None else False,
            }
            for row in rows
        ]

    async def has_permission(
        self,
        session: AsyncSession,
        *,
        role_id: int,
        chamber_id: str, 
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
                    ChamberModules.active_ind == True,
                    RolePermissions.deleted_ind.is_(False),
                )
            )
        )

        self._log_stmt(stmt, session)
        result = await self.execute( session=session, stmt=stmt)
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
        elif action == "import":
            return perm.allow_all_ind or perm.import_ind
        elif action == "export":
            return perm.allow_all_ind or perm.export_ind

        return False
    
    async def get_all_roles_permissions_summary(
        self,
        session: AsyncSession,
        chamber_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get summary of all roles with their permission counts.
        Useful for admin overview of all roles in the chamber.
        """
        # Get all active roles for this chamber
        stmt = (
            select(
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                ChamberRoles.description,
                ChamberRoles.status_ind,
                func.count(RolePermissions.chamber_module_id).label("total_modules"),
                func.sum(
                    (RolePermissions.read_ind.is_(True)).cast(
                        Integer
                    )
                ).label("modules_with_access"),
            )
            .outerjoin(
                RolePermissions,
                and_(
                    ChamberRoles.role_id == RolePermissions.role_id,
                    RolePermissions.chamber_module_id.in_(
                        select(ChamberModules.chamber_module_id).where(
                            ChamberModules.chamber_id == chamber_id,
                            ChamberModules.active_ind.is_(True),
                        )
                    ),
                ),
            )
            .where(
                and_(
                    ChamberRoles.deleted_ind.is_(False),
                    ChamberRoles.chamber_id==chamber_id
                )
            )
            .group_by(
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                ChamberRoles.description,
                ChamberRoles.status_ind,
            )
            .order_by(ChamberRoles.role_name)
        )

        result = await self.execute( session=session, stmt=stmt)
        rows = result.all()

        return [
            {
                "role_id": row.role_id,
                "role_name": row.role_name,
                "description": row.description,
                "status_ind": row.status_ind,
                "total_modules": row.total_modules or 0,
                "modules_with_access": row.modules_with_access or 0,
            }
            for row in rows
        ]

    # ✅ NEW: Get all roles with full permission matrix
    async def get_all_roles_full_matrix(
        self,
        session: AsyncSession,
        chamber_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get complete permission matrix for ALL roles in the chamber.
        Returns flattened structure for easy UI rendering.
        """
        stmt = (
            select(
                ChamberRoles.role_id,
                ChamberRoles.role_name,
                RolePermissions.permission_id,
                RolePermissions.chamber_module_id,
                RolePermissions.allow_all_ind,
                RolePermissions.read_ind,
                RolePermissions.write_ind,
                RolePermissions.create_ind,
                RolePermissions.delete_ind,
                RolePermissions.import_ind,  # ✅ NEW
                RolePermissions.export_ind,  # ✅ NEW
                RefmModules.code.label("module_code"),
                RefmModules.name.label("module_name"),
                RefmModules.sort_order,
            )
            .join(
                RolePermissions,
                ChamberRoles.role_id == RolePermissions.role_id,
            )
            .join(
                ChamberModules,
                RolePermissions.chamber_module_id == ChamberModules.chamber_module_id,
            )
            .join(
                RefmModules,
                ChamberModules.module_code == RefmModules.code,
            )
            .where(
                ChamberRoles.deleted_ind.is_(False),
                ChamberModules.chamber_id == chamber_id,
                ChamberModules.active_ind.is_(True),
            )
            .order_by(
                ChamberRoles.role_name,
                RefmModules.sort_order,
            )
        )

        result = await self.execute( session=session, stmt=stmt)
        rows = result.all()

        return [
            {
                "role_id": row.role_id,
                "role_name": row.role_name,
                "permission_id": row.permission_id,
                "chamber_module_id": row.chamber_module_id,
                "allow_all_ind": row.allow_all_ind,
                "read_ind": row.read_ind,
                "write_ind": row.write_ind,
                "create_ind": row.create_ind,
                "delete_ind": row.delete_ind,
                "import_ind": row.import_ind,  # ✅ NEW
                "export_ind": row.export_ind,  # ✅ NEW
                "module_code": row.module_code,
                "module_name": row.module_name,
                "sort_order": row.sort_order,
            }
            for row in rows
        ]