from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chamber_roles import ChamberRoles
from app.database.models.user_roles import UserRoles
from app.database.repositories.security_roles_repository import SecurityRolesRepository
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
        security_roles_repo: Optional[SecurityRolesRepository] = None,
    ):
        super().__init__(session)
        self.security_roles_repo = security_roles_repo or SecurityRolesRepository()

    async def roles_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[bool] = None,
    ) -> PagingData[RoleWithStatsOut]:
        """Paginated roles with active user count."""
        stmt = (
            select(
                ChamberRoles,
                func.count(UserRoles.user_role_id).label("user_count"),
            )
            .outerjoin(
                UserRoles,
                and_(
                    ChamberRoles.role_id == UserRoles.chamber_role_id,
                    UserRoles.end_date.is_(None),
                ),
            )
            .where(ChamberRoles.is_deleted.is_(False))
            .group_by(ChamberRoles.role_id)
        )

        if search and search.strip():
            stmt = stmt.where(ChamberRoles.role_name.ilike(f"%{search.strip()}%"))

        if status is not None:
            stmt = stmt.where(ChamberRoles.status_ind == status)

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one() or 0

        stmt = stmt.order_by(ChamberRoles.role_name.asc())
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        roles = [
            RoleWithStatsOut(
                role_id=role_row.chamber_role_id,
                description=role_row.description,
                status_ind=role_row.status_ind,
                user_count=user_count or 0,
            )
            for role_row, user_count in rows
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=roles)

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        role = await self.security_roles_repo.get_by_id(
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
        existing = await self.security_roles_repo.get_first(
            self.session,
            filters={ChamberRoles.role_name: payload.role_name.strip()},
            where=[ChamberRoles.is_deleted.is_(False)],
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role name '{payload.role_name}' already exists",
            )

        # ✅ FIXED: Check role code (ALL roles, including deleted)
        if payload.role_code:
            # ❌ DON'T USE: get_first() - applies soft-delete filter
            # ✅ USE: Raw query to check ALL roles
            stmt = select(ChamberRoles).where(
                ChamberRoles.role_code == payload.role_code.upper()
            )
            result = await self.session.execute(stmt)
            existing_code = result.scalars().first()
            
            if existing_code:
                if existing_code.is_deleted:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role code '{payload.role_code}' was previously used by a deleted role. "
                            f"Please use a different code.",
                    )
                else:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role code '{payload.role_code}' already exists",
                    )

        role = await self.security_roles_repo.create(
            session=self.session,
            data={
                "role_name": payload.role_name.strip(),
                "role_code": (payload.role_code or "").upper() or None,
                "description": payload.description,
                "status_ind": payload.status_ind if payload.status_ind is not None else True,
            },
        )
        return RoleOut.model_validate(role)

    async def roles_update(self, role_id: int, payload: RoleUpdate) -> RoleOut:
        existing = await self.security_roles_repo.get_by_id(
            session=self.session, id_values=role_id
        )
        if not existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )

        # ✅ Check role name (non-deleted only, excluding current role)
        if payload.role_name:
            duplicate = await self.security_roles_repo.get_first(
                self.session,
                filters={ChamberRoles.role_name: payload.role_name.strip()},
                where=[
                    ChamberRoles.role_id != role_id,
                    ChamberRoles.is_deleted.is_(False),
                ],
            )
            if duplicate:
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role name '{payload.role_name}' already exists",
                )

        # ✅ FIXED: Check role code (ALL roles, including deleted)
        if payload.role_code:
            stmt = select(ChamberRoles).where(
                ChamberRoles.role_code == payload.role_code.upper(),
                ChamberRoles.role_id != role_id,
            )
            result = await self.session.execute(stmt)
            duplicate_code = result.scalars().first()
            
            if duplicate_code:
                if duplicate_code.is_deleted:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role code '{payload.role_code}' was previously used by a deleted role. "
                            f"Please use a different code.",
                    )
                else:
                    raise ValidationErrorDetail(
                        code=ErrorCodes.VALIDATION_ERROR,
                        message=f"Role code '{payload.role_code}' already exists",
                    )

        update_data: dict = {}
        if payload.role_name is not None:
            update_data["role_name"] = payload.role_name.strip()
        if payload.role_code is not None:
            update_data["role_code"] = payload.role_code.upper()
        if payload.description is not None:
            update_data["description"] = payload.description
        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        if not update_data:
            return RoleOut.model_validate(existing)

        updated_role = await self.security_roles_repo.update(
            session=self.session, id_values=role_id, data=update_data
        )
        return RoleOut.model_validate(updated_role)

    async def roles_delete(self, role_id: int) -> bool:
        role = await self.security_roles_repo.get_by_id(
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

        await self.security_roles_repo.delete(
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
        roles = await self.security_roles_repo.list_all(
            session=self.session,
            where=[ChamberRoles.is_deleted.is_(False), ChamberRoles.status_ind.is_(True)],
            order_by=[ChamberRoles.role_name.asc()],
        )
        return [RoleOut.model_validate(r) for r in roles]
