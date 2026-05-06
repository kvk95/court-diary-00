


from sqlalchemy import func, select, case

from app.database.models.chamber_roles import ChamberRoles
from app.database.models.security_roles import SecurityRoles
from app.database.models.security_roles import SecurityRoles
from app.database.repositories.base.base_repository import BaseRepository
from app.database.repositories.base.repo_context import apply_repo_context


@apply_repo_context
class SecurityRolesRepository(BaseRepository[SecurityRoles]):
    """
    Repository for SecurityRoles model.
    Note: SecurityRoles is a GLOBAL table (not scoped to chamber).
    """

    def __init__(self):
        super().__init__(SecurityRoles)

    async def get_role_stats(self, session):
        stmt = select(
            func.count().label("total_roles"),
            func.sum(case((SecurityRoles.system_ind == True, 1), else_=0)).label("default_roles"),
            func.sum(case((SecurityRoles.admin_ind == True, 1), else_=0)).label("protected_roles"),
        ).where(SecurityRoles.deleted_ind.is_(False))

        row = (await session.execute(stmt)).one()

        return {
            "total_roles": row.total_roles or 0,
            "default_roles": row.default_roles or 0,
            "protected_roles": row.protected_roles or 0,
        }

    def roles_select_stmt(self):
        stmt = (
            select(
                SecurityRoles.role_id,
                SecurityRoles.role_code,
                SecurityRoles.role_name,
                SecurityRoles.description,
                SecurityRoles.system_ind,
                SecurityRoles.admin_ind,
                SecurityRoles.status_ind,
                func.count(func.distinct(ChamberRoles.role_id)).label("chambers_count"),
            )
            .outerjoin(
                ChamberRoles,
                ChamberRoles.security_role_id == SecurityRoles.role_id
            )
            .where(SecurityRoles.deleted_ind.is_(False))
            .group_by(SecurityRoles.role_id)
        )
        return stmt
    
    async def get_by_role_id(self, session, role_id:int):
        stmt = self.roles_select_stmt()
        stmt = stmt.where(SecurityRoles.role_id == role_id)
        row = (await self.execute(session=session, stmt=stmt)).first()

        if not row:
            return None

        return {
                "role_id": row.role_id,
                "role_code": row.role_code,
                "role_name": row.role_name,
                "description": row.description,
                "system_ind": row.system_ind,
                "admin_ind": row.admin_ind,
                "status_ind": row.status_ind,
                "chambers_count": row.chambers_count or 0,
            }
    
    async def list_roles(self, session, page, limit, search):
        stmt = self.roles_select_stmt()

        if search:
            stmt = stmt.where(SecurityRoles.role_name.ilike(f"%{search}%"))
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        rows = (await self.execute(session=session,
                                  stmt=stmt)).scalars().all()
        rows = (await session.execute(stmt)).all()        

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.execute_scalar(session=session, stmt=count_stmt))

        result = []
        for r in rows:
            result.append({
                "role_id": r.role_id,
                "role_code": r.role_code,
                "role_name": r.role_name,
                "description": r.description,
                "system_ind": r.system_ind,
                "admin_ind": r.admin_ind,
                "status_ind": r.status_ind,
                "chambers_count": r.chambers_count or 0,
            })

        return result, total
    
    async def count(self, session):
        stmt = select(func.count(SecurityRoles.role_id)).where(
            SecurityRoles.deleted_ind.is_(False)
        )

        return await self.execute_scalar(session=session,stmt=stmt)