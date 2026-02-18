"""dependencies"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.database.models.base.session import get_session
from app.services.anonymous_service import AnonymousService
from app.services.auth_service import AuthService
from app.services.jobs.invoice_generator_service import InvoiceGeneratorService
from app.services.jobs.pdf_report_service import PdfReportService
from app.services.users_service import UsersService


def get_anonymous_service(
    session: AsyncSession = Depends(get_session),
) -> AnonymousService:
    return AnonymousService(session=session)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


def get_users_service(
    session: AsyncSession = Depends(get_session),
    # Ensures the route is authenticated without passing user explicitly
    _=Depends(get_current_user),
) -> UsersService:
    return UsersService(session=session)


def get_invoice_generator_service(
    session: AsyncSession = Depends(get_session),
) -> InvoiceGeneratorService:
    return InvoiceGeneratorService(session)


def get_pdf_report_service(
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
) -> PdfReportService:
    return PdfReportService(session)
