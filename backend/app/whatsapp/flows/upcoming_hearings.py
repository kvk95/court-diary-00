# app/whatsapp/flows/upcoming_hearings.py

from app.services.calendar_service import CalendarService
from app.whatsapp.formatter import format_upcoming_hearings


async def handle_upcoming_hearings(calendar_service: CalendarService) -> str:
    events = await calendar_service.calendar_get_upcoming()
    return format_upcoming_hearings(events)