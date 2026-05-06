# app/whatsapp/flows/search_case.py

from app.services.cases_service import CasesService
from app.whatsapp.session_store import set, clear, set_search_results, pick_search_result
from app.whatsapp.formatter import format_case_search_results, format_case_detail


class SearchCaseSteps:
    QUERY = "query"
    PICK = "pick"


# ── Start ─────────────────────────────────────────────────────────────────────

async def start_search_case(phone: str) -> str:
    set(phone, {
        "flow": "search_case",
        "step": SearchCaseSteps.QUERY,
        "data": {}
    })
    return "🔍 Enter case number or party name to search"


# ── Handle ────────────────────────────────────────────────────────────────────

async def handle_search_case(
    phone: str,
    message: str,
    session: dict,
    cases_service: CasesService,
) -> str:
    step = session["step"]

    # 1. Search query
    if step == SearchCaseSteps.QUERY:
        query = message.strip()
        if not query:
            return "❌ Please enter a case number or party name"

        # Uses GET /api/cases/cases/lookup?search=... (purpose-built for quick search)
        results = await cases_service.list_cases_for_quick_hearing(search=query, limit=8)

        if not results:
            clear(phone)
            return "🔍 No cases found. Try a different search term.\n\nType MENU to go back."

        # Store result list in session so user can pick by number
        search_results = [
            {
                "case_id": c.case_id,
                "label": f"{c.case_number} — {c.petitioner} vs {c.respondent}",
            }
            for c in results
        ]
        set_search_results(phone, search_results)
        session["step"] = SearchCaseSteps.PICK

        return format_case_search_results(results)

    # 2. User picks a number → show full detail
    elif step == SearchCaseSteps.PICK:
        picked = pick_search_result(phone, message)
        if not picked:
            total = len(session.get("search_results", []))
            return f"❌ Enter a number between 1 and {total}"

        case_id = picked["case_id"]
        case = await cases_service.cases_get_by_id(case_id=case_id)

        clear(phone)
        return format_case_detail(case)

    clear(phone)
    return "❌ Something went wrong. Type MENU to restart."