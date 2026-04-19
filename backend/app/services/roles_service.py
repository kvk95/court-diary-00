from typing import Optional, Dict, Any

from sqlalchemy import and_, func, or_, select
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
        role_code: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[bool] = None,
    ) -> PagingData[RoleWithStatsOut]:
        """Paginated roles with active user count."""
        # Read-only: No logging
        total, rows = await self.chamber_roles_repo.get_roles_paged(
            session=self.session,
            page=page,
            limit= limit, 
            role_code=role_code,
            chamber_id=self.chamber_id,
            search=search, 
            status=status)

        roles = [
            RoleWithStatsOut(
                role_id=role_row.role_id,
                role_code=role_row.role_code,
                role_name=role_row.role_name,
                description=role_row.description,
                status_ind=role_row.status_ind,
                user_count=user_count or 0,
                admin_ind=role_row.admin_ind,
            )
            for role_row, user_count in rows
        ]

        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=roles)

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        # Read-only: No logging
        role = await self.chamber_roles_repo.get_by_id(
            session=self.session, id_values=role_id
        )
        if not role:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND, message=f"Role {role_id} not found"
            )
        return RoleOut.model_validate(role)

    async def roles_add(self, payload: RoleCreate) -> RoleOut:
        if not payload.role_code or not payload.role_code.strip():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role code is required"
            )
        if not payload.role_name or not payload.role_name.strip():
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Role name is required"
            )

        role_code = payload.role_code.strip()
        role_name = payload.role_name.strip()

        # ✅ Check active duplicate
        existing = await self.chamber_roles_repo.get_first(
            self.session,
            where=[
                ChamberRoles.deleted_ind.is_(False),
                or_(
                    ChamberRoles.role_name == role_name,
                    ChamberRoles.role_code == role_code,
                ),
            ],
        )
        if existing:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"Role code '{role_code}' or Role name '{role_name}' already exists",
            )

        # ✅ Check including deleted
        stmt = select(ChamberRoles).where(
            ChamberRoles.role_name == role_code,
            ChamberRoles.chamber_id == self.chamber_id
        )
        result = await self.session.execute(stmt)
        existing_code = result.scalars().first()

        if existing_code:
            if existing_code.deleted_ind:
                # 🔥 Revive Soft-Deleted Role
                await self.chamber_roles_repo.undelete(
                    session=self.session,
                    id_values=existing_code.role_id
                )

                revived = await self.chamber_roles_repo.update(
                    session=self.session,
                    id_values=existing_code.role_id,
                    data={
                        "description": payload.description,
                        "status_ind": payload.status_ind if payload.status_ind is not None else True,
                    }
                )

                await self.log_entity_change(
                    action="Role revived",
                    entity_type="role",
                    entity_id=str(revived.role_id),
                    extra_metadata={"role_name": role_name}
                )

                return RoleOut.model_validate(revived)
            else:
                # This branch is theoretically unreachable if the active check above is correct
                raise ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Role code '{role_code}' already exists",
                )

        # ✅ CREATE new role
        role = await self.chamber_roles_repo.create(
            session=self.session,
            data={
                "role_code": role_code,
                "role_name": role_name,
                "description": payload.description,
                "status_ind": payload.status_ind if payload.status_ind is not None else True,
            },
        )

        await self.log_entity_change(
            action="Role created",
            entity_type="role",
            entity_id=str(role.role_id),
            payload=payload
        )

        return RoleOut.model_validate(role)

    async def roles_update(self, role_id: int, payload: RoleUpdate) -> RoleOut:
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

        # 🔹 Handle role_name
        if payload.role_name and payload.role_name.strip():
            new_name = payload.role_name.strip()

            # Active duplicate check (excluding current role)
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

            # Soft-deleted duplicate check
            stmt = select(ChamberRoles).where(
                ChamberRoles.chamber_id == self.chamber_id,
                ChamberRoles.role_name == new_name,
                ChamberRoles.role_id != role_id,
                ChamberRoles.deleted_ind.is_(True)
            )

            result = await self.chamber_roles_repo.execute(stmt, self.session)
            soft_deleted_duplicate = result.scalars().first()

            if soft_deleted_duplicate:
                # 🔥 Edge Case: Resurrect the deleted duplicate instead of updating current role
                revived = await self.chamber_roles_repo.update(
                    session=self.session,
                    id_values=soft_deleted_duplicate.role_id,
                    data={
                        "deleted_ind": False,
                        "role_name": new_name,
                        "description": payload.description,
                        "status_ind": payload.status_ind if payload.status_ind is not None else True,
                    }
                )
                
                await self.log_entity_change(
                    action="Role revived and updated",
                    entity_type="role",
                    entity_id=str(soft_deleted_duplicate.role_id),
                    extra_metadata={
                        "role_name": new_name,
                        "reason": "Name conflict resolution: Revived soft-deleted duplicate"
                    }
                )

                return RoleOut.model_validate(revived)

            update_data["role_name"] = new_name

        # 🔹 Other fields
        if payload.description is not None:
            update_data["description"] = payload.description

        if payload.status_ind is not None:
            update_data["status_ind"] = payload.status_ind

        # ✅ No changes
        if not update_data:
            return RoleOut.model_validate(existing)

        # ✅ Normal update
        updated = await self.chamber_roles_repo.update(
            session=self.session,
            id_values=role_id,
            data=update_data
        )

        await self.log_entity_change(
            action="Role updated",
            entity_type="role",
            entity_id=str(role_id),
            payload=payload,
            extra_metadata={"updated_fields": list(update_data.keys())}
        )

        return RoleOut.model_validate(updated)

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
            and_(UserRoles.role_id == role_id, UserRoles.end_date.is_(None))
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
        
        await self.log_entity_change(
            action="Role deleted",
            entity_type="role",
            entity_id=str(role_id),
            extra_metadata={"role_name": role.role_name}
        )
        return True

    async def get_role_stats(self, role_id: int) -> RoleUserCountOut:
        # Read-only: No logging
        stmt = select(func.count(UserRoles.user_role_id)).where(
            and_(UserRoles.role_id == role_id, UserRoles.end_date.is_(None))
        )
        result = await self.session.execute(stmt)
        user_count = result.scalar_one() or 0
        return RoleUserCountOut(role_id=role_id, user_count=user_count)

    async def get_all_roles(self) -> list[RoleOut]:
        # Read-only: No logging
        roles = await self.chamber_roles_repo.list_all(
            session=self.session,
            where=[ChamberRoles.deleted_ind.is_(False), 
                   ChamberRoles.status_ind.is_(True)
                   ,ChamberRoles.chamber_id == self.chamber_id],
            order_by=[ChamberRoles.role_name.asc()],
        )
        return [RoleOut.model_validate(r) for r in roles]