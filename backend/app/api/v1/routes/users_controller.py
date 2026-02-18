from typing import Dict, List

from fastapi import Body, Depends, Path, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_users_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.users_dto import (
    RoleCreate,
    RoleDelete,
    RoleOut,
    RolePermissionEdit,
    RolePermissionOut,
    RoleUpdate,
    UserCreate,
    UserEdit,
    UserOut,
)
from app.services.users_service import UsersService
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class UsersController(BaseController):
    CONTROLLER_NAME = "users"

    # ── SECURITY ROLES ─────────────────────────────────────────────────────
    @BaseController.get(
        "/roles/paged",
        summary="Get roles (paginated)",
        response_model=BaseOutDto[PagingData[RoleOut]],
    )
    async def security_roles_get_paged(
        self,
        page: int = Query(
            PAGINATION_DEFAULT_PAGE, ge=1, le=10_000, description="Page number"
        ),
        limit: int = Query(
            PAGINATION_DEFAULT_LIMIT, ge=1, le=1000, description="Items per page"
        ),
        role_name: str | None = Query(None, description="Filter by role name"),
        status: bool | None = Query(None, description="Filter by status"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[PagingData[RoleOut]]:
        data: PagingData[RoleOut] = await service.security_roles_get_paged(
            page, limit, role_name, status
        )
        return self.success(result=data)

    @BaseController.post(
        "/roles/add",
        summary="Add new role",
        response_model=BaseOutDto[RoleOut],
    )
    async def security_roles_add(
        self,
        payload: RoleCreate = Body(..., description="Role creation data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[RoleOut]:
        result: RoleOut = await service.security_roles_add(payload)
        return self.success(result=result)

    @BaseController.put(
        "/roles/edit",
        summary="Update role",
        response_model=BaseOutDto[RoleOut],
    )
    async def security_roles_update(
        self,
        payload: RoleUpdate = Body(..., description="Updated role data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[RoleOut]:
        result: RoleOut = await service.security_roles_update(payload)
        return self.success(result=result)

    @BaseController.delete(
        "/roles/delete",
        summary="Delete role",
        response_model=BaseOutDto[dict],
    )
    async def security_roles_delete(
        self,
        payload: RoleDelete = Body(..., description="Delete role data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        await service.security_roles_delete(payload)
        return self.success(result={}, description="Role deleted successfully")

    # ── ROLE PERMISSIONS ───────────────────────────────────────────────────
    @BaseController.get(
        "/role/{role_id}/permissions",
        summary="Get role permissions",
        response_model=BaseOutDto[List[RolePermissionOut]],
    )
    async def role_permissions_get_all(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        module_name: str | None = Query(None, description="Filter by module"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[List[RolePermissionOut]]:
        result: List[RolePermissionOut] = await service.role_permissions_get_all(
            role_id, module_name
        )
        return self.success(result=result)

    @BaseController.put(
        "/role/{role_id}/permissions/edit",
        summary="Edit role permissions",
        response_model=BaseOutDto[bool],
    )
    async def role_permissions_edit(
        self,
        role_id: int = Path(..., gt=0, description="Role ID"),
        payload: list[RolePermissionEdit] = Body(..., description="Permissions to set"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[bool]:
        result: bool = await service.role_permissions_edit(role_id, payload)
        return self.success(result=result)

    # ── USERS ──────────────────────────────────────────────────────────────
    @BaseController.get(
        "/user/paged",
        summary="Get users (paginated)",
        response_model=BaseOutDto[PagingData[UserOut]],
    )
    async def users_get_paged(
        self,
        page: int = Query(
            PAGINATION_DEFAULT_PAGE, ge=1, le=10_000, description="Page number"
        ),
        limit: int = Query(
            PAGINATION_DEFAULT_LIMIT, ge=1, le=1000, description="Items per page"
        ),
        search: str | None = Query(None, description="Search by name/email/username"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[PagingData[UserOut]]:
        result: PagingData[UserOut] = await service.users_get_paged(page, limit, search)
        return self.success(result=result)

    @BaseController.post(
        "/user/add",
        summary="Add user",
        response_model=BaseOutDto[int],
    )
    async def users_add(
        self,
        payload: UserCreate = Body(..., description="New user data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[int]:
        result: int = await service.users_add(payload)
        return self.success(result=result)

    @BaseController.put(
        "/user/{user_id}/edit",
        summary="Edit user",
        response_model=BaseOutDto[bool],
    )
    async def users_edit(
        self,
        user_id: int = Path(..., gt=0, description="User ID"),
        payload: UserEdit = Body(..., description="Updated user data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[bool]:
        result: bool = await service.users_edit(user_id, payload)
        return self.success(result=result)

    @BaseController.delete(
        "/user/{user_id}/delete",
        summary="Delete user",
        response_model=BaseOutDto[dict],
    )
    async def users_delete(
        self,
        user_id: int = Path(..., gt=0, description="User ID"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        return self.success(result={})
        # await service.users_delete(user_id)
        # return self.success(result={}, description="User deleted successfully")

    @BaseController.put(
        "/defaultstore",
        summary="Set default store",
        response_model=BaseOutDto[bool],
    )
    async def user_default_store(
        self,
        payload: Dict = Body(...),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[bool]:
        result: bool = await service.user_default_store(payload)
        return self.success(result=result)
