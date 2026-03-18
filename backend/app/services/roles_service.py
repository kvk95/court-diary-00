from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.security_roles import SecurityRoles
from app.database.models.user_roles import UserRoles
from app.database.repositories.role_permissions_repository import RolePermissionsRepository
from app.database.repositories.security_roles_repository import SecurityRolesRepository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.roles_dto import (
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithStatsOut,
    RoleUserCountOut,
)
from app.validators import ErrorCodes, ValidationErrorDetail

from .base.secured_base_service import BaseSecuredService


class RolesService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        security_roles_repo: Optional[SecurityRolesRepository] = None,
        role_permissions_repo: Optional[RolePermissionsRepository] = None,
    ):
        super().__init__(session)
        self.security_roles_repo = security_roles_repo or SecurityRolesRepository()
        self.role_permissions_repo = role_permissions_repo or RolePermissionsRepository()

    # ── Roles Listing with Stats ─────────────────────────────────────
    async def roles_get_paged(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        status: bool | None = None,
    ) -> PagingData[RoleWithStatsOut]:
        """
        Get paginated roles with user counts and stats.
        """
        # Build base query with user count
        stmt = (
            select(
                SecurityRoles,
                func.count(UserRoles.user_role_id).label("user_count"),
            )
            .outerjoin(UserRoles, and_(
                SecurityRoles.role_id == UserRoles.role_id,
                UserRoles.end_date == None,
            ))
            .where(
                SecurityRoles.is_deleted.is_(False),
            )
            .group_by(SecurityRoles.role_id)
        )

        # Apply filters
        if search:
            stmt = stmt.where(
                SecurityRoles.role_name.ilike(f"%{search}%")
            )
        
        if status is not None:
            stmt = stmt.where(SecurityRoles.status_ind == status)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        # Apply ordering and pagination
        stmt = stmt.order_by(SecurityRoles.role_name.asc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        # Build response
        roles = []
        for role_row, user_count in rows:
            roles.append(RoleWithStatsOut(
                role_id=role_row.role_id,
                role_name=role_row.role_name,
                role_code=role_row.role_code,
                description=role_row.description,
                status_ind=role_row.status_ind,
                user_count=user_count or 0,
            ))

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=roles)

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        """Get single role by ID."""
        role = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
        )
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Role {role_id} not found"
            )
        return RoleOut.model_validate(role)

    async def roles_add(self, payload: RoleCreate) -> RoleOut:
        """Create new role."""
        # Validate role_name
        if not payload.role_name:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role name is required"
            )

        # Check for duplicate role_name
        existing = await self.security_roles_repo.get_first(
            self.session,
            filters={SecurityRoles.role_name: payload.role_name},  # ✅ Equality only
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role name '{payload.role_name}' already exists"
            )

        # Check for duplicate role_code if provided
        if payload.role_code:
            existing_code = await self.security_roles_repo.get_first(
                self.session,
                filters={SecurityRoles.role_code: payload.role_code},  # ✅ Equality only
            )
            if existing_code:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role code '{payload.role_code}' already exists"
                )

        # Create role
        role_data = {
            "role_name": payload.role_name,
            "role_code": payload.role_code,
            "description": payload.description,
            "status_ind": payload.status_ind if payload.status_ind is not None else True,
        }

        role = await self.security_roles_repo.create(
            session=self.session,
            data=role_data,
        )
        return RoleOut.model_validate(role)

    async def roles_update(self, role_id: int, payload: RoleUpdate) -> RoleOut:
        """Update existing role."""
        # Check if role exists
        existing = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
        )
        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Role {role_id} not found"
            )

        # Check for duplicate role_name (excluding current role)
        if payload.role_name:
            # ✅ FIX: Use where clause for inequality, filters for equality
            duplicate = await self.security_roles_repo.get_first(
                self.session,
                filters={
                    SecurityRoles.role_name: payload.role_name,  # ✅ Equality in filters
                },
                where=[
                    SecurityRoles.role_id != role_id,  # ✅ Inequality in where
                    SecurityRoles.is_deleted.is_(False),
                ],
            )
            if duplicate:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name '{payload.role_name}' already exists"
                )

        # Check for duplicate role_code (excluding current role)
        if payload.role_code:
            duplicate_code = await self.security_roles_repo.get_first(
                self.session,
                filters={
                    SecurityRoles.role_code: payload.role_code,  # ✅ Equality in filters
                },
                where=[
                    SecurityRoles.role_id != role_id,  # ✅ Inequality in where
                    SecurityRoles.is_deleted.is_(False),
                ],
            )
            if duplicate_code:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role code '{payload.role_code}' already exists"
                )

        # Update role
        update_data = {}
        if payload.role_name is not None:
            update_data["role_name"] = payload.role_name
        if payload.role_code is not None:
            update_data["role_code"] = payload.role_code
        if payload.description is not None:
            update_data["description"] = payload.description
        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        updated_role = await self.security_roles_repo.update(
            session=self.session,
            id_values=role_id,
            data=update_data,
        )
        return RoleOut.model_validate(updated_role)

    async def roles_delete(self, role_id: int) -> bool:
        """Soft delete a role."""
        role = await self.security_roles_repo.get_by_id(
            session=self.session,
            id_values=role_id,
        )
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message=f"Role {role_id} not found"
            )

        # Check if role is in use
        stmt = select(func.count(UserRoles.user_role_id)).where(
            and_(
                UserRoles.role_id == role_id,
                UserRoles.end_date == None,
            )
        )
        result = await self.session.execute(stmt)
        user_count = result.scalar_one() or 0

        if user_count > 0:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Cannot delete role: {user_count} user(s) are assigned to this role"
            )

        # Soft delete
        await self.security_roles_repo.delete(
            session=self.session,
            filters={SecurityRoles.role_id: role_id},
            soft=True,
        )
        return True

    async def get_role_stats(self, role_id: int) -> RoleUserCountOut:
        """Get role statistics (user count, etc.)."""
        # Count active users with this role
        stmt = select(func.count(UserRoles.user_role_id)).where(
            and_(
                UserRoles.role_id == role_id,
                UserRoles.end_date == None,
            )
        )
        result = await self.session.execute(stmt)
        user_count = result.scalar_one() or 0

        return RoleUserCountOut(
            role_id=role_id,
            user_count=user_count,
        )