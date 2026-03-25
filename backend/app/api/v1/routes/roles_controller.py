# app/api/v1/routes/roles_controller.py

from typing import List, Optional

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_roles_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.roles_dto import (
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleUserCountOut,
    RoleWithStatsOut,
)
from app.services.roles_service import RolesService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class RolesController(BaseController):
    CONTROLLER_NAME = "roles"

    # ─────────────────────────────────────────────────────────────────────────
    # 1. List Roles (Paginated with Stats)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/paged",
        summary="Get roles (paginated with stats)",
        response_model=BaseOutDto[PagingData[RoleWithStatsOut]],
    )
    async def roles_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1, le=10_000),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=1000),
        search: Optional[str] = Query(None, description="Search by role name"),
        status: Optional[bool] = Query(None, description="Filter by active status"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[PagingData[RoleWithStatsOut]]:
        data = await service.roles_get_paged(page, limit, search, status)
        return self.success(result=data)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Get All Active Roles (For Dropdowns)
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/all",
        summary="Get all active roles (for dropdowns)",
        response_model=BaseOutDto[List[RoleOut]],
    )
    async def get_all_roles(
        self,
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[List[RoleOut]]:
        result = await service.get_all_roles()
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Get Role by ID
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{role_id}",
        summary="Get role by ID",
        response_model=BaseOutDto[RoleOut],
    )
    async def get_role_by_id(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result = await service.get_role_by_id(role_id)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Add New Role
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.post(
        "/add",
        summary="Add new role",
        response_model=BaseOutDto[RoleOut],
    )
    async def roles_add(
        self,
        payload: RoleCreate = Body(...),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result = await service.roles_add(payload)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Update Role
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/{role_id}/edit",
        summary="Update role",
        response_model=BaseOutDto[RoleOut],
    )
    async def roles_update(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        payload: RoleUpdate = Body(...),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleOut]:
        result = await service.roles_update(role_id, payload)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Delete Role
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.delete(
        "/{role_id}/delete",
        summary="Delete role (soft delete, blocked if users assigned)",
        response_model=BaseOutDto[bool],
    )
    async def roles_delete(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[bool]:
        result = await service.roles_delete(role_id)
        return self.success(result=result)

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Get Role Statistics
    # ─────────────────────────────────────────────────────────────────────────

    @BaseController.get(
        "/{role_id}/stats",
        summary="Get role statistics (user count)",
        response_model=BaseOutDto[RoleUserCountOut],
    )
    async def get_role_stats(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        service: RolesService = Depends(get_roles_service),
    ) -> BaseOutDto[RoleUserCountOut]:
        result = await service.get_role_stats(role_id)
        return self.success(result=result)