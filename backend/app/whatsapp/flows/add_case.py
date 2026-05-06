# app/whatsapp/flows/add_case.py

from datetime import datetime
from app.database.models.refm_case_status import RefmCaseStatusConstants
from app.dtos.cases_dto import CaseCreate, CourtItem
from app.services.cases_service import CasesService
from app.whatsapp.session_store import set, clear
from app.whatsapp.formatter import format_court_selection, format_case_confirmation, format_case_created


class AddCaseSteps:
    CASE_NUMBER = "case_number"
    STATE = "state"
    COURT = "court"
    PETITIONER = "petitioner"
    RESPONDENT = "respondent"
    NEXT_HEARING_DATE = "next_hearing_date"
    CONFIRM = "confirm"


def map_input_to_court(message: str, courts: list[CourtItem]) -> CourtItem | None:
    try:
        index = int(message) - 1
        return courts[index]
    except (ValueError, IndexError):
        return None


def parse_date(text: str):
    return datetime.strptime(text.strip(), "%d-%m-%Y").date()


# ── Start ─────────────────────────────────────────────────────────────────────

async def start_add_case(phone: str) -> str:
    set(phone, {
        "flow": "add_case",
        "step": AddCaseSteps.CASE_NUMBER,
        "data": {}
    })
    return "📄 Enter Case Number"


# ── Handle ────────────────────────────────────────────────────────────────────

async def handle_add_case(
    phone: str,
    message: str,
    session: dict,
    cases_service: CasesService,
) -> str:
    step = session["step"]
    data = session["data"]

    # 1. Case Number
    if step == AddCaseSteps.CASE_NUMBER:
        if not message.strip():
            return "❌ Case number is required"
        data["case_number"] = message.strip()
        session["step"] = AddCaseSteps.STATE
        return "Enter 2-digit state code (e.g. TN, MH, DL)"

    # 2. State → fetch courts
    if step == AddCaseSteps.STATE:
        if not message.strip() or len(message.strip()) != 2:
            return "❌ Invalid state code. Enter exactly 2 letters (e.g. TN)"
        state = message.strip().upper()
        courts: list[CourtItem] = await cases_service.get_courts(
            limit=10,
            search=None,
            state_code=state,
            court_type_code=None,
        )
        if not courts:
            return f"❌ No courts found for state '{state}'. Try a different code."
        session["courts"] = courts
        session["step"] = AddCaseSteps.COURT
        return format_court_selection(courts)

    # 3. Court
    elif step == AddCaseSteps.COURT:
        court = map_input_to_court(message, session.get("courts", []))
        if not court:
            return "❌ Invalid selection. Enter a valid number from the list"
        data["court_code"] = court.court_code
        session["step"] = AddCaseSteps.PETITIONER
        return "👤 Enter Petitioner Name"

    # 4. Petitioner
    elif step == AddCaseSteps.PETITIONER:
        if not message.strip():
            return "❌ Petitioner name is required"
        data["petitioner"] = message.strip()
        session["step"] = AddCaseSteps.RESPONDENT
        return "👤 Enter Respondent Name"

    # 5. Respondent
    elif step == AddCaseSteps.RESPONDENT:
        if not message.strip():
            return "❌ Respondent name is required"
        data["respondent"] = message.strip()
        session["step"] = AddCaseSteps.NEXT_HEARING_DATE
        return "📅 Enter Next Hearing Date (DD-MM-YYYY) or type SKIP"

    # 6. Hearing date
    elif step == AddCaseSteps.NEXT_HEARING_DATE:
        if message.strip().lower() != "skip":
            try:
                data["next_hearing_date"] = parse_date(message)
            except ValueError:
                return "❌ Invalid date. Use DD-MM-YYYY or type SKIP"
        session["step"] = AddCaseSteps.CONFIRM
        return format_case_confirmation(data)

    # 7. Confirm
    elif step == AddCaseSteps.CONFIRM:
        if message.strip().lower() not in ["yes", "y"]:
            clear(phone)
            return "❌ Cancelled. Type MENU to go back."

        payload = CaseCreate(**data)
        payload.status_code = RefmCaseStatusConstants.ACTIVE

        await cases_service.cases_add(payload=payload)
        clear(phone)
        return format_case_created(data)

    return "❌ Something went wrong. Type MENU to restart."