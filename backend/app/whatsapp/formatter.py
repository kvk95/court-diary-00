# app/whatsapp/formatter.py

from app.dtos.cases_dto import CourtItem


# ── Main Menu ─────────────────────────────────────────────────────────────────

def main_menu() -> str:
    return (
        "👋 *NyaDesk*\n\n"
        "1. Add Case\n"
        "2. Today's Hearings\n"
        "3. This Month's Hearings\n"
        "4. Upcoming Hearings\n"
        "5. Search Case\n"
        "6. Add Hearing\n"
        "7. Add Note\n"
        "8. Update Case Status\n"
        "9. Dashboard\n\n"
        "Type *MENU* anytime to return here"
    )


# ── Add Case ──────────────────────────────────────────────────────────────────

def format_court_selection(courts: list[CourtItem]) -> str:
    msg = "🏛 Select Court:\n\n"
    for i, c in enumerate(courts, 1):
        msg += f"{i}. {c.court_name}\n"
    msg += "\nReply with number"
    return msg


def format_case_confirmation(data: dict) -> str:
    return (
        "📄 *Confirm Case*\n\n"
        f"Case: {data['case_number']}\n"
        f"Court: {data['court_code']}\n"
        f"👤 {data['petitioner']} vs {data['respondent']}\n"
        f"📅 {data.get('next_hearing_date', 'N/A')}\n\n"
        "Reply *YES* to confirm or *NO* to cancel"
    )


def format_case_created(data: dict) -> str:
    return (
        "✅ *Case Added*\n\n"
        f"📁 {data['case_number']}\n"
        f"👤 {data['petitioner']} vs {data['respondent']}\n"
        f"🏛 {data.get('court_code', '')}\n"
        f"📅 Next hearing: {data.get('next_hearing_date', 'Not set')}"
    )


# ── Calendar / Hearings ───────────────────────────────────────────────────────

def format_today_hearings(events) -> str:
    if not events:
        return "📅 No hearings today"

    msg = "📅 *Today's Hearings*\n\n"
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


def format_month_hearings(result) -> str:
    events = result.events
    if not events:
        return "📅 No hearings this month"

    msg = "📅 *This Month's Hearings*\n\n"
    msg += f"Total: {result.total_hearings}\n"
    msg += f"Upcoming: {result.upcoming_count}\n"
    msg += f"Completed: {result.completed_count}\n\n"

    for i, e in enumerate(events[:10], 1):
        msg += (
            f"{i}. {e.event_date.strftime('%d-%b')}\n"
            f"   {e.case_number}\n"
            f"   🏛 {e.court_name or ''}\n\n"
        )
    if len(events) > 10:
        msg += f"...and {len(events) - 10} more\n"
    return msg


def format_upcoming_hearings(events) -> str:
    if not events:
        return "📅 No upcoming hearings"

    msg = "📅 *Upcoming Hearings*\n\n"
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


def format_range_hearings(events, title: str = "📅 Hearings") -> str:
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


# ── Case Search ───────────────────────────────────────────────────────────────

def format_case_search_results(cases: list) -> str:
    """cases is a list of CaseListOut / CaseQuickHearingOut objects."""
    if not cases:
        return "🔍 No cases found. Try a different search term."

    msg = "🔍 *Search Results*\n\n"
    for i, c in enumerate(cases, 1):
        msg += f"{i}. {c.case_number}\n"
        msg += f"   {c.petitioner} vs {c.respondent}\n"
        if hasattr(c, "court_name") and c.court_name:
            msg += f"   🏛 {c.court_name}\n"
        if hasattr(c, "status_description") and c.status_description:
            msg += f"   🔖 {c.status_description}\n"
        msg += "\n"
    msg += "Reply with number to view details"
    return msg


def format_case_detail(c) -> str:
    """c is a CaseDetailOut object."""
    msg = (
        f"📁 *{c.case_number}*\n\n"
        f"👤 {c.petitioner}\n"
        f"   vs {c.respondent}\n\n"
        f"🏛 {c.court_name or c.court_code}\n"
        f"🔖 {c.status_description or c.status_code or 'N/A'}\n"
    )
    if c.next_hearing_date:
        msg += f"📅 Next: {c.next_hearing_date}\n"
    if c.last_hearing_date:
        msg += f"📅 Last: {c.last_hearing_date}\n"
    msg += (
        f"\n📊 Hearings: {c.total_hearings}  "
        f"Notes: {c.total_notes}  "
        f"Clients: {c.linked_clients}\n"
    )
    return msg


# ── Add Hearing ───────────────────────────────────────────────────────────────

def format_hearing_confirmation(data: dict, case_number: str) -> str:
    return (
        "📅 *Confirm Hearing*\n\n"
        f"Case: {case_number}\n"
        f"Date: {data['hearing_date']}\n"
        f"Purpose: {data.get('purpose_description', 'Not set')}\n\n"
        "Reply *YES* to confirm or *NO* to cancel"
    )


def format_hearing_created(case_number: str, hearing_date) -> str:
    return (
        "✅ *Hearing Added*\n\n"
        f"📁 {case_number}\n"
        f"📅 {hearing_date}"
    )


# ── Add Note ──────────────────────────────────────────────────────────────────

def format_note_confirmation(case_number: str, note_text: str) -> str:
    preview = note_text[:100] + ("..." if len(note_text) > 100 else "")
    return (
        "📝 *Confirm Note*\n\n"
        f"Case: {case_number}\n"
        f"Note: {preview}\n\n"
        "Reply *YES* to save or *NO* to cancel"
    )


def format_note_created(case_number: str) -> str:
    return f"✅ Note saved for *{case_number}*"


# ── Update Case Status ────────────────────────────────────────────────────────

def format_status_confirmation(case_number: str, new_status: str) -> str:
    return (
        f"Update *{case_number}* status to *{new_status}*?\n\n"
        "Reply *YES* to confirm or *NO* to cancel"
    )


def format_status_updated(case_number: str, new_status: str) -> str:
    return f"✅ *{case_number}* status updated to *{new_status}*"


# ── Dashboard ─────────────────────────────────────────────────────────────────

def format_dashboard(d) -> str:
    """d is a MainDashboardOut object."""
    msg = (
        f"👋 *{d.greeting}, {d.user_first_name}*\n\n"
        f"📁 Active cases: {d.active_cases_count}\n"
        f"📅 Today's hearings: {d.today_hearings_count}\n"
    )

    if d.overdue_cases:
        msg += f"\n⚠️ *Overdue ({len(d.overdue_cases)})*\n"
        for c in d.overdue_cases[:3]:
            msg += f"  • {c.case_number} — {c.petitioner}\n"
        if len(d.overdue_cases) > 3:
            msg += f"  ...and {len(d.overdue_cases) - 3} more\n"

    if d.todays_hearings:
        msg += f"\n📅 *Today*\n"
        for h in d.todays_hearings[:5]:
            msg += f"  • {h.case_number} — {h.petitioner} vs {h.respondent}\n"
            if h.purpose_description:
                msg += f"    📌 {h.purpose_description}\n"

    if d.tomorrows_hearings:
        msg += f"\n📅 *Tomorrow*\n"
        for h in d.tomorrows_hearings[:5]:
            msg += f"  • {h.case_number} — {h.petitioner} vs {h.respondent}\n"

    return msg


# ── Keep old name for backward compat ─────────────────────────────────────────
# (add_case.py currently imports format_confirmation)
format_confirmation = format_case_confirmation