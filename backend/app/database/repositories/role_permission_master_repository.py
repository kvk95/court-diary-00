
from sqlalchemy import distinct, select, func

from app.database.models.refm_modules import RefmModules
from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.role_permission_master import RolePermissionMaster

@apply_repo_context
class RolePermissionMasterRepository(BaseRepository[RolePermissionMaster]):
    def __init__(self):
        super().__init__(RolePermissionMaster)

    async def count_distinct_modules(self, session):

        stmt = select(
            func.count(
                distinct(RolePermissionMaster.module_code)
            )
        )

        return await self.execute_scalar(session=session, stmt=stmt)
    
    async def get_by_role(self, session, role_id: int):

        stmt = (
            select(
                RolePermissionMaster.id,
                RolePermissionMaster.module_code,

                RolePermissionMaster.allow_all_ind,

                RolePermissionMaster.read_ind,
                RolePermissionMaster.write_ind,
                RolePermissionMaster.create_ind,
                RolePermissionMaster.delete_ind,

                RolePermissionMaster.import_ind,
                RolePermissionMaster.export_ind,

                RefmModules.description.label("module_name"),
            )
            .join(
                RefmModules,
                RefmModules.code == RolePermissionMaster.module_code
            )
            .where(
                RolePermissionMaster.security_role_id == role_id
            )
        )

        result = await self.execute(session=session, stmt=stmt)

        return result.all()
    
    async def get_last_updated(self, session):

        stmt = select(
            func.max(
                func.coalesce(
                    RolePermissionMaster.updated_date,
                    RolePermissionMaster.created_date
                )
            ).label("last_pushed")
        )
        result = await self.execute(session=session, stmt=stmt)
        return result.first()