# app/whatsapp/flows/dashboard.py

from app.dtos.oauth_dtos import CurrentUserContext
from app.services.dashboard_service import DashboardService
from app.whatsapp.formatter import format_dashboard


async def handle_dashboard(dashboard_service: DashboardService,current_user: CurrentUserContext) -> str:
    first_name = current_user.first_name or "there"
    data = await dashboard_service.get_main_dashboard(user_first_name=first_name)
    return format_dashboard(data)