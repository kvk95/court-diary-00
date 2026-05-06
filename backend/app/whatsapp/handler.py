# app/whatsapp/handler.py

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base.secured_base_service import BaseSecuredService
from app.services.calendar_service import CalendarService
from app.services.cases_service import CasesService
from app.services.dashboard_service import DashboardService
from app.whatsapp.flow_registry import FLOW_REGISTRY, START_REGISTRY
from app.whatsapp.menu_map import MENU_MAP
from app.whatsapp.session_store import get, clear
from app.whatsapp.formatter import main_menu

# Flows
from app.whatsapp.flows.today_hearings import handle_today_hearings
from app.whatsapp.flows.month_hearings import handle_month_hearings
from app.whatsapp.flows.upcoming_hearings import handle_upcoming_hearings
from app.whatsapp.flows.dashboard import handle_dashboard


_GLOBAL_COMMANDS = {"menu", "0", "cancel", "quit", "exit"}


class WhatsAppService(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        cases_service: Optional[CasesService] = None,
        calendar_service: Optional[CalendarService] = None,
        dashboard_service: Optional[DashboardService] = None,
    ):
        super().__init__(session)
        self.cases_service = cases_service or CasesService(session=session)
        self.calendar_service = calendar_service or CalendarService(session=session)
        self.dashboard_service = dashboard_service or DashboardService(session=session)

    async def handle_message(self, phone: str, message: str) -> str:
        msg = message.strip()
        msg_lower = msg.lower()

        # ── Global reset ─────────────────────────────────────
        if msg_lower in _GLOBAL_COMMANDS:
            clear(phone)
            return main_menu()

        session = get(phone)

        # ── Active flow ─────────────────────────────────────
        if session:
            flow = session.get("flow","")

            handler = FLOW_REGISTRY.get(flow)
            if handler:
                return await handler(
                    phone,
                    msg,
                    session,
                    self.cases_service,
                )

            clear(phone)
            return main_menu()

        # ── Start new flow ───────────────────
        flow_name = MENU_MAP.get(msg_lower)

        if flow_name:
            starter = START_REGISTRY.get(flow_name)
            if starter:
                return await starter(phone)

        # ── Non-flow actions ─────────────────
        if msg_lower in ("2", "today hearings"):
            return await handle_today_hearings(self.calendar_service)

        if msg_lower in ("3", "month hearings"):
            return await handle_month_hearings(self.calendar_service)

        if msg_lower in ("4", "upcoming"):
            return await handle_upcoming_hearings(self.calendar_service)

        if msg_lower in ("9", "dashboard"):
            return await handle_dashboard(self.dashboard_service, self.current_user)

        return main_menu()

        return main_menu()