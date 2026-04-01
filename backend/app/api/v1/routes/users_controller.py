# app/api/v1/routes/users_controller.py

from typing import Optional
from fastapi import Body, Depends, Path, Query
from app.database.models.refm_user_deletion_status import RefmUserDeletionStatusEnum
from app.dtos.users_dto import (
    UserOut, 
    UserCreate, 
    UserEdit, 
    UserStatusToggle, 
    DeletionRejectPayload,
    DeletionRequestOut,
    UserStatsOut
)
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.services.users_service import UsersService
from app.dependencies import get_current_user, get_users_service
from app.api.v1.routes.base.base_controller import BaseController
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE


class UsersController(BaseController):
    CONTROLLER_NAME = "users"

    # ── List/Paged (FIRST - before parameterized routes) ─────────────────────

    @BaseController.get(
        "/stats",
        summary="Get user management statistics",
        response_model=BaseOutDto[UserStatsOut],
    )
    async def users_get_stats(
        self,
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserStatsOut]:
        """Get statistics for user management dashboard."""
        result = await service.get_user_stats()
        return self.success(result=result)

    @BaseController.get(
        "/paged",
        summary="Get users (paginated)",
        response_model=BaseOutDto[PagingData[UserOut]],
    )
    async def users_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1, description="Page number"),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500, description="Items per page"),
        search: Optional[str] = Query(None, description="Search by name, email, phone, role"),
        status_ind: Optional[bool] = Query(None, description="None -> All, true -> Active, false -> InActive"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[PagingData[UserOut]]:
        data = await service.users_get_paged(page=page, limit=limit, search=search,status_ind=status_ind)
        return self.success(result=data)

    # ── Current User (SECOND - before parameterized routes) ──────────────────
    @BaseController.get(
        "/me",
        summary="Get current user with full profile and permissions",
        response_model=BaseOutDto[UserOut],
    )
    async def users_get_me(
        self,
        current_user: UserOut = Depends(get_current_user),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserOut]: 
        result = await service.users_get_by_id(
            user_id=current_user.user_id,
        )
        return self.success(result=result)

    # ── Single by ID (LAST - parameterized routes) ───────────────────────────
    @BaseController.get(
        "/{user_id}",
        summary="Get user by ID with full profile and permissions",
        response_model=BaseOutDto[UserOut], 
    )
    async def users_get_by_id(
        self,
        user_id: str = Path(..., min_length=36, max_length=36),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserOut]: 
        result = await service.users_get_by_id(
            user_id=user_id,
        )
        return self.success(result=result)

    # ── Add ───────────────────────────────────────────────────────────────────

    @BaseController.post(
        "/add",
        summary="Add user to chamber",
        response_model=BaseOutDto[UserOut],
    )
    async def users_add(
        self,
        payload: UserCreate = Body(..., description="New user data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserOut]:
        result: UserOut = await service.users_add(payload)
        return self.success(result=result)

    # ── Edit ──────────────────────────────────────────────────────────────────

    @BaseController.put(
        "/{user_id}/edit",
        summary="Edit user",
        response_model=BaseOutDto[UserOut],
    )
    async def users_edit(
        self,
        user_id: str = Path(..., min_length=36, max_length=36),
        payload: UserEdit = Body(..., description="Fields to update"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserOut]:
        result = await service.users_edit(user_id=user_id, payload=payload)
        return self.success(result=result)

    # ── Status Toggle ─────────────────────────────────────────────────────────

    @BaseController.put(
        "/status",
        summary="Activate or deactivate a user",
        response_model=BaseOutDto[UserOut],
    )
    async def users_toggle_status(
        self,
        payload: UserStatusToggle = Body(...),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[UserOut]:
        result = await service.users_toggle_status(payload=payload)
        return self.success(result=result)

    # ── Delete (request) ──────────────────────────────────────────────────────

    @BaseController.delete(
        "/{user_id}/delete",
        summary="Request user deletion (creates approval request)",
        response_model=BaseOutDto[dict],
    )
    async def users_delete(
        self,
        user_id: str = Path(..., min_length=36, max_length=36),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        result = await service.users_delete(user_id=user_id)
        return self.success(result=result)

    # ── Deletion Requests ─────────────────────────────────────────────────────

    @BaseController.get(
        "/deletion-requests/paged",
        summary="Get deletion requests (admin)",
        response_model=BaseOutDto[PagingData[DeletionRequestOut]],
    )
    async def get_deletion_requests(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=500),
        status: Optional[RefmUserDeletionStatusEnum] = Query(None),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[PagingData[DeletionRequestOut]]:
        data = await service.get_deletion_requests(page=page, limit=limit, status=status)
        return self.success(result=data)

    @BaseController.put(
        "/deletion-requests/{request_id}/approve",
        summary="Approve deletion request (admin)",
        response_model=BaseOutDto[dict],
    )
    async def approve_deletion_request(
        self,
        request_id: int = Path(..., gt=0, description="Deletion request ID"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        result = await service.approve_deletion_request(request_id=request_id)
        return self.success(result=result)

    @BaseController.put(
        "/deletion-requests/{request_id}/reject",
        summary="Reject deletion request (admin)",
        response_model=BaseOutDto[dict],
    )
    async def reject_deletion_request(
        self,
        request_id: int = Path(..., gt=0, description="Deletion request ID"),
        payload: DeletionRejectPayload = Body(..., description="Fields to reject deletion"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        result = await service.reject_deletion_request(
            request_id=request_id, payload=payload
        )
        return self.success(result=result)

    # ── Add / Remove user from Chamber (soft-delete link) ────────────────────────────
    
    @BaseController.post(
        "/{user_id}/add-to-chamber",
        summary="Add user to this chamber",
        response_model=BaseOutDto[dict],
    )
    async def users_add_to_chamber(
        self,
        user_id: str = Path(..., min_length=36, max_length=36),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        result = await service.users_add_to_chamber(user_id=user_id)
        return self.success(result=result)

    @BaseController.delete(
        "/{user_id}/remove-from-chamber",
        summary="Remove user from this chamber (preserves user account)",
        response_model=BaseOutDto[dict],
    )
    async def users_remove_from_chamber(
        self,
        user_id: str = Path(..., min_length=36, max_length=36),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[dict]:
        result = await service.users_remove_from_chamber(user_id=user_id)
        return self.success(result=result)
