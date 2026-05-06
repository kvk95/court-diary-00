# app/whatsapp/flows/update_case_status.py

from app.dtos.cases_dto import CaseEdit
from app.services.cases_service import CasesService
from app.whatsapp.wrefm_cache import wrefm_cache_instance
from app.whatsapp.session_store import set, clear, set_search_results, pick_search_result
from app.whatsapp.formatter import (
    format_case_search_results,
    format_status_confirmation,
    format_status_updated,
)


class UpdateStatusSteps:
    SEARCH = "search"
    PICK_CASE = "pick_case"
    PICK_STATUS = "pick_status"
    CONFIRM = "confirm"


# ── Start ─────────────────────────────────────────────────────────────────────

async def start_update_case_status(phone: str) -> str:
    set(phone, {
        "flow": "update_case_status",
        "step": UpdateStatusSteps.SEARCH,
        "data": {}
    })
    return "🔖 *Update Case Status*\n\n🔍 Enter case number or party name"


# ── Handle ────────────────────────────────────────────────────────────────────

async def handle_update_case_status(
    phone: str,
    message: str,
    session: dict,
    cases_service: CasesService,
) -> str:
    step = session["step"]
    data = session["data"]

    # 1. Search
    if step == UpdateStatusSteps.SEARCH:
        query = message.strip()
        if not query:
            return "❌ Please enter a case number or party name"

        results = await cases_service.list_cases_for_quick_hearing(search=query, limit=8)
        if not results:
            return "🔍 No cases found. Try a different search term."

        set_search_results(phone, [
            {
                "case_id": c.case_id,
                "case_number": c.case_number,
                "status_code": getattr(c, "status_code", None),
                "label": f"{c.case_number} — {c.petitioner} vs {c.respondent}",
            }
            for c in results
        ])
        session["step"] = UpdateStatusSteps.PICK_CASE
        return format_case_search_results(results)

    # 2. Pick case
    elif step == UpdateStatusSteps.PICK_CASE:
        picked = pick_search_result(phone, message)
        if not picked:
            total = len(session.get("search_results", []))
            return f"❌ Enter a number between 1 and {total}"

        data["case_id"] = picked["case_id"]
        data["case_number"] = picked["case_number"]
        current_code = picked.get("status_code")

        status_menu = wrefm_cache_instance.format_case_status_menu(current_code=current_code)
        if not status_menu:
            clear(phone)
            return "❌ Status options not available right now. Try again later."

        session["step"] = UpdateStatusSteps.PICK_STATUS
        return f"📁 *{picked['case_number']}*\n\n{status_menu}"

    # 3. Pick new status
    elif step == UpdateStatusSteps.PICK_STATUS:
        picked = wrefm_cache_instance.pick_case_status(message)
        if not picked:
            total = len(wrefm_cache_instance.case_statuses)
            return f"❌ Enter a number between 1 and {total}"

        data["status_code"] = picked["code"]
        data["status_description"] = picked["description"]
        session["step"] = UpdateStatusSteps.CONFIRM
        return format_status_confirmation(data["case_number"], picked["description"])

    # 4. Confirm
    elif step == UpdateStatusSteps.CONFIRM:
        if message.strip().lower() not in ["yes", "y"]:
            clear(phone)
            return "❌ Cancelled. Type MENU to go back."

        payload = CaseEdit(
            case_id=data["case_id"],
            status_code=data["status_code"],
        )
        await cases_service.cases_edit(payload=payload)
        case_number = data["case_number"]
        status_description = data["status_description"]
        clear(phone)
        return format_status_updated(case_number, status_description)

    clear(phone)
    return "❌ Something went wrong. Type MENU to restart."