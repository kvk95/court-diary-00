from datetime import date
from app.services.calendar_service import CalendarService
from app.whatsapp.formatter import format_month_hearings


async def handle_month_hearings(calendar_service: CalendarService):
    today = date.today()

    result = await calendar_service.calendar_get_month(
        year=today.year,
        month=today.month
    )

    return format_month_hearings(result)