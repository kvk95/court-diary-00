# app/whatsapp/flows/add_hearing.py

from app.dtos.cases_dto import HearingCreate
from app.services.cases_service import CasesService
from app.utils.utilities import parse_date
from app.whatsapp.wrefm_cache import wrefm_cache_instance
from app.whatsapp.session_store import set, clear, set_search_results, pick_search_result
from app.whatsapp.formatter import (
    format_case_search_results,
    format_hearing_confirmation,
    format_hearing_created,
)


class AddHearingSteps:
    SEARCH = "search"
    PICK_CASE = "pick_case"
    DATE = "date"
    PURPOSE = "purpose"
    CONFIRM = "confirm"


# ── Start ─────────────────────────────────────────────────────────────────────

async def start_add_hearing(phone: str) -> str:
    set(phone, {
        "flow": "add_hearing",
        "step": AddHearingSteps.SEARCH,
        "data": {}
    })
    return "📅 *Add Hearing*\n\n🔍 Enter case number or party name"


# ── Handle ────────────────────────────────────────────────────────────────────

async def handle_add_hearing(
    phone: str,
    message: str,
    session: dict,
    cases_service: CasesService,
) -> str:
    step = session["step"]
    data = session["data"]

    # 1. Search for case
    if step == AddHearingSteps.SEARCH:
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
        session["step"] = AddHearingSteps.PICK_CASE
        return format_case_search_results(results)

    # 2. Pick case from results
    elif step == AddHearingSteps.PICK_CASE:
        picked = pick_search_result(phone, message)
        if not picked:
            total = len(session.get("search_results", []))
            return f"❌ Enter a number between 1 and {total}"

        data["case_id"] = picked["case_id"]
        data["case_number"] = picked["case_number"]
        session["step"] = AddHearingSteps.DATE
        return f"📁 *{picked['case_number']}*\n\n📅 Enter hearing date (DD-MM-YYYY)"

    # 3. Hearing date
    elif step == AddHearingSteps.DATE:
        try:
            data["hearing_date"] = parse_date(message)
        except ValueError:
            return "❌ Invalid date. Use DD-MM-YYYY (e.g. 15-06-2025)"

        # Show purpose menu if available, otherwise skip straight to confirm
        purpose_menu = wrefm_cache_instance.format_hearing_purpose_menu()
        if purpose_menu:
            session["step"] = AddHearingSteps.PURPOSE
            return purpose_menu
        else:
            # No purposes loaded — skip to confirm
            session["step"] = AddHearingSteps.CONFIRM
            return format_hearing_confirmation(data, data["case_number"])

    # 4. Purpose (optional)
    elif step == AddHearingSteps.PURPOSE:
        if message.strip().lower() != "skip":
            picked = wrefm_cache_instance.pick_hearing_purpose(message)
            if not picked:
                return f"❌ Invalid selection. Enter a number from the list or type SKIP"
            data["purpose_code"] = picked["code"]
            data["purpose_description"] = picked["description"]

        session["step"] = AddHearingSteps.CONFIRM
        return format_hearing_confirmation(data, data["case_number"])

    # 5. Confirm
    elif step == AddHearingSteps.CONFIRM:
        if message.strip().lower() not in ["yes", "y"]:
            clear(phone)
            return "❌ Cancelled. Type MENU to go back."

        payload = HearingCreate(
            case_id=data["case_id"],
            hearing_date=parse_date(str(data["hearing_date"])),
            status_code=wrefm_cache_instance.default_hearing_status_code,
            purpose_code=data.get("purpose_code"),
            notes=None,
            order_details=None,
            next_hearing_date=None,
        )
        await cases_service.hearings_add(payload=payload)
        case_number = data["case_number"]
        hearing_date = data["hearing_date"]
        clear(phone)
        return format_hearing_created(case_number, hearing_date)

    clear(phone)
    return "❌ Something went wrong. Type MENU to restart."