"""dependencies"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.database.models.base.session import get_session
from app.services.anonymous_service import AnonymousService
from app.services.auth_service import AuthService
from app.services.cases_service import CasesService
from app.services.clients_service import ClientsService
from app.services.invitations_service import InvitationsService


from app.services.role_permissions_service import RolePermissionsService
from app.services.roles_service import RolesService
from app.services.users_service import UsersService



def get_anonymous_service(
    session: AsyncSession = Depends(get_session),
) -> AnonymousService:
    return AnonymousService(session=session)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)

def get_cases_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> CasesService:
    return CasesService(session=session)


async def get_roles_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> RolesService:
    return RolesService(
        session=session,
    )


async def get_role_permissions_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> RolePermissionsService:
    return RolePermissionsService(
        session=session,
    )


async def get_users_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> UsersService:
    return UsersService(
        session=session
    )

async def get_clients_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> ClientsService:
    return ClientsService(
        session=session
    )

async def get_invitations_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> InvitationsService:
    return InvitationsService(
        session=session
    )