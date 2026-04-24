# app/whatsapp/formatter.py

from app.dtos.cases_dto import CourtItem


def main_menu():
    return """👋 Welcome

1. Add Case
2. Today Hearings
3. This Month Hearings
4. Add Note
5. Case Status
"""


def format_court_selection(courts:list[CourtItem]):
    msg = "🏛 Select Court:\n\n"
    for i, c in enumerate(courts, 1):
        msg += f"{i}. {c.court_name}\n"
    msg += "\nReply with number"
    return msg


def format_confirmation(data):
    return f"""
📄 Confirm Case

Case: {data['case_number']}
Court: {data['court_code']}
👤 {data['petitioner']} vs {data['respondent']}
📅 {data.get('next_hearing_date', 'N/A')}

Reply YES to confirm
"""

def format_today_hearings(events):
    if not events:
        return "📅 No hearings today"

    msg = "📅 Today Hearings\n\n"

    for i, e in enumerate(events, 1):
        msg += (
            f"{i}. {e.case_number}\n"
            f"   {e.petitioner} vs {e.respondent}\n"
            f"   🏛 {e.court_name or ''}\n"
        )

        if e.purpose_description:
            msg += f"   📌 {e.purpose_description}\n"

        if e.status_description:
            msg += f"   🔖 {e.status_description}\n"

        msg += "\n"

    return msg

def format_month_hearings(result):
    events = result.events

    if not events:
        return "📅 No hearings this month"

    msg = "📅 This Month Hearings\n\n"

    msg += f"Total: {result.total_hearings}\n"
    msg += f"Upcoming: {result.upcoming_count}\n"
    msg += f"Completed: {result.completed_count}\n\n"

    # 🔥 Limit output (VERY IMPORTANT for WhatsApp)
    for i, e in enumerate(events[:10], 1):
        msg += (
            f"{i}. {e.event_date.strftime('%d-%b')}\n"
            f"   {e.case_number}\n"
            f"   🏛 {e.court_name or ''}\n\n"
        )

    if len(events) > 10:
        msg += f"...and {len(events) - 10} more\n"

    return msg

def format_range_hearings(events, title="📅 Hearings"):
    if not events:
        return f"{title}\n\nNo hearings found"

    msg = f"{title}\n\n"

    for i, e in enumerate(events[:10], 1):
        msg += (
            f"{i}. {e.event_date.strftime('%d-%b')}\n"
            f"   {e.case_number}\n"
            f"   {e.petitioner} vs {e.respondent}\n"
            f"   🏛 {e.court_name or ''}\n"
        )

        if e.purpose_description:
            msg += f"   📌 {e.purpose_description}\n"

        msg += "\n"

    if len(events) > 10:
        msg += f"...and {len(events) - 10} more\n"

    return msg