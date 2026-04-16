
from enum import Enum as PyEnum
from typing import Callable, cast

from fastapi import Depends

from app.auth.deps import get_current_user
from app.core.context import get_request_context
from app.database.models.refm_modules import RefmModulesEnum
from app.dtos.oauth_dtos import CurrentUserContext
from app.dtos.users_dto import UserOut
from app.validators import ValidationErrorDetail, ErrorCodes


class PermissionTypeEnum(str, PyEnum):
    READ   = "read"
    WRITE  = "write"
    CREATE = "create"
    DELETE = "delete"
    IMPORT = "import"
    EXPORT = "export"


PType = PermissionTypeEnum  # convenience alias


def require_permission(module: RefmModulesEnum, permission: PType) -> Callable:
    """
    Dependency factory that enforces module-level permission.
    Reads from request context cache — no extra DB hit.

    Usage:
        Depends(require_permission(RefmModulesEnum.CASES, PType.READ))
    """
    perm_key = f"{permission.value}_ind"

    async def _check(
        current_user: CurrentUserContext = Depends(get_current_user),
    ) -> CurrentUserContext:

        ctx = get_request_context() or {}
        ctx_user_details = ctx.get("user_details")

        if not ctx_user_details:
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message="User details not loaded",
            )
        
        user_details:UserOut = cast(UserOut, ctx_user_details)

        permissions: list = user_details.permissions

        module_perm = next(
            (p for p in permissions if p.module_code == module.value),
            None,
        )

        if not module_perm:
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message=f"No access to module '{module.value}'",
            )

        if module_perm.allow_all_ind:
            return current_user

        if not getattr(module_perm, perm_key, False):
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message=f"No '{permission.value}' permission on module '{module.value}'",
            )

        return current_user

    return _check