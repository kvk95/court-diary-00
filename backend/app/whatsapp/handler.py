# app/whatsapp/handler.py

from app.services.calendar_service import CalendarService
from app.services.cases_service import CasesService
from app.whatsapp.flows.month_hearings import handle_month_hearings
from app.whatsapp.flows.today_hearings import handle_today_hearings
from app.whatsapp.session_store import get
from app.whatsapp.formatter import main_menu
from app.whatsapp.flows.add_case import start_add_case, handle_add_case


async def handle_message(phone: str, message: str, cases_service:CasesService, calendar_service:CalendarService):
    session = get(phone)

    # 🟢 NEW USER
    if not session:
        if message.lower() in ["1", "add case"]:
            return await start_add_case(phone)
        
        if message.lower() in ["2", "today hearings"]:
            return await handle_today_hearings(calendar_service)
        
        if message.lower() in ["3", "this month hearings"]:
            return await handle_month_hearings(calendar_service)

        return main_menu()

    # 🟢 ACTIVE FLOW
    if session["flow"] == "add_case":
        return await handle_add_case(phone, message, session, cases_service)

    return "❌ Something went wrong"