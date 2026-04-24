from datetime import date
from app.services.calendar_service import CalendarService
from app.whatsapp.formatter import format_today_hearings


async def handle_today_hearings(calendar_service: CalendarService):
    today = date.today()

    events = await calendar_service.calendar_get_range(
        date_from=today,
        date_to=today
    )

    return format_today_hearings(events)