"""dependencies.py — FastAPI service factories"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.auth.permissions import PType, require_permission
from app.database.models.refm_modules import RefmModulesEnum
from app.database.models.base.session import get_session

from app.services.anonymous_service import AnonymousService
from app.services.auth_service import AuthService
from app.services.chamber_service import ChamberService
from app.services.contact_messages_service import ContactMessagesService
from app.services.image_service import ImageService
from app.services.calendar_service import CalendarService
from app.services.cases_service import CasesService
from app.services.clients_service import ClientsService
from app.services.role_permissions_service import RolePermissionsService
from app.services.roles_service import RolesService
from app.services.support_ticket_service import SupportTicketService
from app.services.users_service import UsersService
from app.services.dashboard_service import DashboardService
from app.services.aor_service import AorService


# ── No-auth services ──────────────────────────────────────────────────────────

def get_anonymous_service(
    session: AsyncSession = Depends(get_session),
) -> AnonymousService:
    return AnonymousService(session=session)

def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(session)


# ── Auth-only services (no specific module restriction) ───────────────────────

async def get_chamber_service(
    session: AsyncSession = Depends(get_session),
    _ = Depends(get_current_user)
) -> ChamberService:
    return ChamberService(session=session)

def get_image_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> ImageService:
    return ImageService(session=session)


# ── Module-gated services ─────────────────────────────────────────────────────

def get_cases_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.CASES, PType.READ)),
) -> CasesService:
    return CasesService(session=session)

def get_aor_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.CASES, PType.READ)),  # AOR lives under CASES
) -> AorService:
    return AorService(session=session)

async def get_clients_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.CLIENTS, PType.READ)),
) -> ClientsService:
    return ClientsService(session=session, image_service=get_image_service())

# async def get_billing_service(
#     session: AsyncSession = Depends(get_session),
#     _=Depends(require_permission(RefmModulesEnum.BILLING, PType.READ)),
# ) -> BillingService:
#     return BillingService(session=session)

async def get_calendar_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.CALENDAR, PType.READ)),
) -> CalendarService:
    return CalendarService(session=session)

# async def get_collaborations_service(
#     session: AsyncSession = Depends(get_session),
#     _=Depends(require_permission(RefmModulesEnum.COLLABORATIONS, PType.READ)),
# ) -> CollaborationsService:
#     return CollaborationsService(session=session)

# async def get_reports_service(
#     session: AsyncSession = Depends(get_session),
#     _=Depends(require_permission(RefmModulesEnum.REPORTS, PType.READ)),
# ) -> ReportsService:
#     return ReportsService(session=session)

async def get_dashboard_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.DASHBOARD, PType.READ)),
) -> DashboardService:
    return DashboardService(session=session)

async def get_users_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.USER_MANAGEMENT, PType.READ)),
) -> UsersService:
    return UsersService(session=session, image_service=get_image_service())

async def get_roles_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.USER_MANAGEMENT, PType.READ)),  # roles live under USER
) -> RolesService:
    return RolesService(session=session)

async def get_role_permissions_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(require_permission(RefmModulesEnum.USER_MANAGEMENT, PType.READ)),  # same
) -> RolePermissionsService:
    return RolePermissionsService(session=session)

async def get_support_ticket_service(
    session: AsyncSession = Depends(get_session),
    _ = Depends(get_current_user)
) -> SupportTicketService:
    return SupportTicketService(session=session)

async def get_contact_messages_service(
    session: AsyncSession = Depends(get_session),
) -> ContactMessagesService:
    return ContactMessagesService(session=session)