# app/whatsapp/flows/add_note.py

from app.dtos.cases_dto import CaseNoteCreate
from app.services.cases_service import CasesService
from app.whatsapp.session_store import set, clear, set_search_results, pick_search_result
from app.whatsapp.formatter import (
    format_case_search_results,
    format_note_confirmation,
    format_note_created,
)


class AddNoteSteps:
    SEARCH = "search"
    PICK_CASE = "pick_case"
    NOTE_TEXT = "note_text"
    CONFIRM = "confirm"


# ── Start ─────────────────────────────────────────────────────────────────────

async def start_add_note(phone: str) -> str:
    set(phone, {
        "flow": "add_note",
        "step": AddNoteSteps.SEARCH,
        "data": {}
    })
    return "📝 *Add Note*\n\n🔍 Enter case number or party name"


# ── Handle ────────────────────────────────────────────────────────────────────

async def handle_add_note(
    phone: str,
    message: str,
    session: dict,
    cases_service: CasesService,
) -> str:
    step = session["step"]
    data = session["data"]

    # 1. Search for case
    if step == AddNoteSteps.SEARCH:
        query = message.strip()
        if not query:
            return "❌ Please enter a case number or party name"

        results = await cases_service.list_cases_for_quick_hearing(search=query, limit=8)
        if not results:
            return "🔍 No cases found. Try a different search term."

        set_search_results(phone, [
            {"case_id": c.case_id, "case_number": c.case_number, "label": f"{c.case_number} — {c.petitioner} vs {c.respondent}"}
            for c in results
        ])
        session["step"] = AddNoteSteps.PICK_CASE
        return format_case_search_results(results)

    # 2. Pick case
    elif step == AddNoteSteps.PICK_CASE:
        picked = pick_search_result(phone, message)
        if not picked:
            total = len(session.get("search_results", []))
            return f"❌ Enter a number between 1 and {total}"

        data["case_id"] = picked["case_id"]
        data["case_number"] = picked["case_number"]
        session["step"] = AddNoteSteps.NOTE_TEXT
        return f"📁 *{picked['case_number']}*\n\n📝 Type your note"

    # 3. Note text
    elif step == AddNoteSteps.NOTE_TEXT:
        note_text = message.strip()
        if not note_text:
            return "❌ Note cannot be empty"
        if len(note_text) > 2000:
            return f"❌ Note too long ({len(note_text)} chars). Keep it under 2000 characters."

        data["note_text"] = note_text
        session["step"] = AddNoteSteps.CONFIRM
        return format_note_confirmation(data["case_number"], note_text)

    # 4. Confirm
    elif step == AddNoteSteps.CONFIRM:
        if message.strip().lower() not in ["yes", "y"]:
            clear(phone)
            return "❌ Cancelled. Type MENU to go back."

        payload = CaseNoteCreate(
            case_id=data["case_id"],
            note_text=data["note_text"],
            private_ind=False,
        )
        await cases_service.case_notes_add(payload=payload)
        case_number = data["case_number"]
        clear(phone)
        return format_note_created(case_number)

    clear(phone)
    return "❌ Something went wrong. Type MENU to restart."