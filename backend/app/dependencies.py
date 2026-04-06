"""dependencies.py — FastAPI service factories"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user

from app.database.models.base.session import get_session
from app.services.anonymous_service import AnonymousService
from app.services.auth_service import AuthService
from app.services.chamber_service import ChamberService
from app.services.image_service import ImageService
from app.services.billing_service import BillingService
from app.services.calendar_service import CalendarService
from app.services.cases_service import CasesService
from app.services.clients_service import ClientsService
from app.services.collaborations_service import CollaborationsService
from app.services.invitations_service import InvitationsService
from app.services.reports_service import ReportsService
from app.services.role_permissions_service import RolePermissionsService
from app.services.roles_service import RolesService
from app.services.users_service import UsersService
from app.services.dashboard_service import DashboardService
from app.services.aor_service import AorService


def get_anonymous_service(session: AsyncSession = Depends(get_session)) -> AnonymousService:
    return AnonymousService(session=session)

def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)

async def get_chamber_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> ChamberService:
    return ChamberService(session=session)

def get_image_service(session: AsyncSession = Depends(get_session), 
                      _=Depends(get_current_user)) -> ImageService:
    return ImageService(session=session)

def get_cases_service(session: AsyncSession = Depends(get_session), 
                      _=Depends(get_current_user)) -> CasesService:
    return CasesService(session=session)

async def get_clients_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> ClientsService:
    return ClientsService(session=session,image_service=get_image_service())

async def get_billing_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> BillingService:
    return BillingService(session=session)

async def get_calendar_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> CalendarService:
    return CalendarService(session=session)

async def get_reports_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> ReportsService:
    return ReportsService(session=session)

async def get_collaborations_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> CollaborationsService:
    return CollaborationsService(session=session)

async def get_invitations_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> InvitationsService:
    return InvitationsService(session=session)

async def get_roles_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> RolesService:
    return RolesService(session=session)

async def get_role_permissions_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> RolePermissionsService:
    return RolePermissionsService(session=session)

async def get_users_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> UsersService:
    return UsersService(session=session,image_service=get_image_service())

async def get_aor_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> AorService:
    return AorService(session=session)

async def get_dashboard_service(session: AsyncSession = Depends(get_session), _=Depends(get_current_user)) -> DashboardService:
    return DashboardService(session=session)
