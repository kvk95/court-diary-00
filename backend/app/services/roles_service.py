from typing import Optional, Dict, Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_roles import ChamberRoles
from app.database.models.user_roles import UserRoles
from app.database.repositories.chamber_roles_repository import ChamberRolesRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.roles_dto import (
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleUserCountOut,
    RoleWithStatsOut,
)
from app.validators import ErrorCodes, ValidationErrorDetail

from .base.secured_base_service import BaseSecuredService


class RolesService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        chamber_roles_repo: Optional[ChamberRolesRepository] = None,
    ):
        super().__init__(session)
        self.chamber_roles_repo = chamber_roles_repo or ChamberRolesRepository()

    async def roles_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[bool] = None,
    ) -> PagingData[RoleWithStatsOut]:
        """Paginated roles with active user count."""
        total, rows = await self.chamber_roles_repo.get_roles_paged(
            session=self.session,
            page=page,
            limit= limit, 
            search=search, 
            status=status)

        roles = [
            RoleWithStatsOut(
                role_id=role_row.role_id,
                role_name=role_row.role_name,
                description=role_row.description,
                status_ind=role_row.status_ind,
                user_count=user_count or 0,
            )
            for role_row, user_count in rows
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=roles)

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        role = await self.chamber_roles_repo.get_by_id(
            session=self.session, id_values=role_id
        )
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )
        return RoleOut.model_validate(role)

    async def roles_add(self, payload: RoleCreate) -> RoleOut:
        if not payload.role_name or not payload.role_name.strip():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR, message="Role name is required"
            )

        # ✅ Check role name (non-deleted only - names can be reused)
        existing = await self.chamber_roles_repo.get_first(
            self.session,
            filters={ChamberRoles.role_name: payload.role_name.strip()},
            where=[ChamberRoles.is_deleted.is_(False)],
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role name '{payload.role_name}' already exists",
            )

        # ✅ Check role name (ALL roles, including deleted)
        if payload.role_name:
            # ❌ DON'T USE: get_first() - applies soft-delete filter
            # ✅ USE: Raw query to check ALL roles
            stmt = select(ChamberRoles).where(
                ChamberRoles.role_name == payload.role_name.upper()
            )
            result = await self.session.execute(stmt)
            existing_code = result.scalars().first()
            
            if existing_code:
                if existing_code.is_deleted:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role name '{payload.role_name}' was previously used by a deleted role. "
                            f"Please use a different code.",
                    )
                else:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role name '{payload.role_name}' already exists",
                    )

        role = await self.chamber_roles_repo.create(
            session=self.session,
            data={
                "role_name": payload.role_name.strip(),
                "description": payload.description,
                "status_ind": payload.status_ind if payload.status_ind is not None else True,
            },
        )
        return RoleOut.model_validate(role)

    async def roles_update(self, role_id: int, payload: RoleUpdate) -> RoleOut:
        """Update existing chamber role with proper duplicate name validation."""
        
        # 1. Fetch existing role
        existing = await self.chamber_roles_repo.get_by_id(
            session=self.session, 
            id_values=role_id
        )
        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, 
                message=f"Role {role_id} not found"
            )

        update_data: Dict[str, Any] = {}

        # 2. Handle role_name change with strict validation
        if payload.role_name and payload.role_name.strip():
            new_name = payload.role_name.strip()

            # Check for duplicate ACTIVE role in the same chamber (excluding current role)
            duplicate = await self.chamber_roles_repo.get_first(
                self.session,
                filters={
                    ChamberRoles.role_name: new_name,
                    ChamberRoles.chamber_id: self.chamber_id
                },
                where=[ChamberRoles.role_id != role_id]
            )

            if duplicate:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name '{new_name}' already exists in this chamber."
                )

            # Check if name was previously used by a soft-deleted role in this chamber
            stmt = select(ChamberRoles).where(
                ChamberRoles.chamber_id == self.chamber_id,
                ChamberRoles.role_name == new_name,
                ChamberRoles.role_id != role_id,
                ChamberRoles.is_deleted.is_(True)
            )
            result = await self.chamber_roles_repo.execute(stmt, self.session)   # ← Use repo.execute
            soft_deleted_duplicate = result.scalars().first()

            if soft_deleted_duplicate:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name '{new_name}' was previously used by a deleted role in this chamber. "
                            f"Please choose a different name."
                )

            update_data["role_name"] = new_name

        # 3. Other fields
        if payload.description is not None:
            update_data["description"] = payload.description

        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        # 4. No changes → return as-is
        if not update_data:
            return RoleOut.model_validate(existing)

        # 5. Perform update using repository upsert (recommended)
        updated_role = await self.chamber_roles_repo.upsert(
            session=self.session,
            id_values=role_id,
            data=update_data
        )

        return RoleOut.model_validate(updated_role)

    async def roles_delete(self, role_id: int) -> bool:
        role = await self.chamber_roles_repo.get_by_id(
            session=self.session, id_values=role_id
        )
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )

        # Block deletion if role has active assignments
        stmt = select(func.count(UserRoles.user_role_id)).where(
            and_(UserRoles.chamber_role_id == role_id, UserRoles.end_date.is_(None))
        )
        result = await self.session.execute(stmt)
        user_count = result.scalar_one() or 0

        if user_count > 0:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Cannot delete role: {user_count} user(s) are currently assigned to it",
            )

        await self.chamber_roles_repo.delete(
            session=self.session, id_values=role_id, soft=True
        )
        return True

    async def get_role_stats(self, role_id: int) -> RoleUserCountOut:
        stmt = select(func.count(UserRoles.user_role_id)).where(
            and_(UserRoles.chamber_role_id == role_id, UserRoles.end_date.is_(None))
        )
        result = await self.session.execute(stmt)
        user_count = result.scalar_one() or 0
        return RoleUserCountOut(role_id=role_id, user_count=user_count)

    async def get_all_roles(self) -> list[RoleOut]:
        """Lightweight list for dropdowns (no pagination needed)."""
        roles = await self.chamber_roles_repo.list_all(
            session=self.session,
            where=[ChamberRoles.is_deleted.is_(False), ChamberRoles.status_ind.is_(True)],
            order_by=[ChamberRoles.role_name.asc()],
        )
        return [RoleOut.model_validate(r) for r in roles]
