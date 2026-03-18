
from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_roles_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.roles_dto import (
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithStatsOut,
    RoleUserCountOut,
)
from app.services.roles_service import RolesService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class RolesController(BaseController):
    CONTROLLER_NAME = "roles"

    # ── Roles Listing ─────────────────────────────────────────────────────
    @BaseController.get(
        "/paged",
        summary="Get roles (paginated with stats)",
        response_model=BaseOutDto[PagingData[RoleWithStatsOut]],
    )
    async def roles_get_paged(
        self,
        page: int = Query(
            PAGINATION_DEFAULT_PAGE, ge=1, le=10_000, description="Page number"
        ),
        limit: int = Query(
            PAGINATION_DEFAULT_LIMIT, ge=1, le=1000, description="Items per page"
        ),
        search: str | None = Query(None, description="Search by role name"),
        status: bool | None = Query(None, description="Filter by status"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[PagingData[RoleWithStatsOut]]:
        data: PagingData[RoleWithStatsOut] = await service.roles_get_paged(
            page, limit, search, status
        )
        return self.success(result=data)

    @BaseController.get(
        "/roles/{role_id}",
        summary="Get role by ID",
        response_model=BaseOutDto[RoleOut],
    )
    async def get_role_by_id(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result: RoleOut = await service.get_role_by_id(role_id)
        return self.success(result=result)

    @BaseController.post(
        "/roles/add",
        summary="Add new role",
        response_model=BaseOutDto[RoleOut],
    )
    async def roles_add(
        self,
        payload: RoleCreate = Body(..., description="Role creation data"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result: RoleOut = await service.roles_add(payload)
        return self.success(result=result)

    @BaseController.put(
        "/roles/{role_id}/edit",
        summary="Update role",
        response_model=BaseOutDto[RoleOut],
    )
    async def roles_update(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        payload: RoleUpdate = Body(..., description="Updated role data"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result: RoleOut = await service.roles_update(role_id, payload)
        return self.success(result=result)

    @BaseController.delete(
        "/roles/{role_id}/delete",
        summary="Delete role (soft delete)",
        response_model=BaseOutDto[bool],
    )
    async def roles_delete(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[bool]:
        result:bool = await service.roles_delete(role_id)
        return self.success(result)

    @BaseController.get(
        "/roles/{role_id}/stats",
        summary="Get role statistics",
        response_model=BaseOutDto[RoleUserCountOut],
    )
    async def get_role_stats(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleUserCountOut]:
        result: RoleUserCountOut = await service.get_role_stats(role_id)
        return self.success(result=result)