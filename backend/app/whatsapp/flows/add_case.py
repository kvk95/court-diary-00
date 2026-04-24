# app/whatsapp/flows/add_case.py

from datetime import datetime
from app.database.models.refm_case_status import RefmCaseStatusConstants
from app.dtos.cases_dto import CaseCreate, CourtItem
from app.services.cases_service import CasesService
from app.whatsapp.session_store import set, clear
from app.whatsapp.formatter import format_court_selection, format_confirmation

class AddCaseSteps:
    CASE_NUMBER = "case_number"
    STATE = "Enter 2 Digit State Code"
    COURT = "court"
    PETITIONER = "petitioner"
    RESPONDENT = "respondent"
    NEXT_HEARING_DATE = "next_hearing_date"
    CONFIRM = "confirm"


def map_input_to_court(message, courts) -> CourtItem | None:
    try:
        index = int(message) - 1
        return courts[index]
    except:
        return None


def parse_date(text: str):
    return datetime.strptime(text, "%d-%m-%Y").date()


# 🚀 START FLOW
async def start_add_case(phone: str):
    set(phone, {
        "flow": "add_case",
        "step": AddCaseSteps.CASE_NUMBER,
        "data": {}
    })

    return "📄 Enter Case Number"


# 🚀 HANDLE FLOW
async def handle_add_case(phone: str, message: str, session: dict, cases_service:CasesService):
    step = session["step"]
    data = session["data"]

    # 1️⃣ CASE NUMBER
    if step == AddCaseSteps.CASE_NUMBER:
        if not message.strip():
            return "❌ Case number is required"

        data["case_number"] = message.strip()
        session["step"] = AddCaseSteps.STATE

        return "Enter 2 digit state code"
    
    if step == AddCaseSteps.STATE:
        if not message.strip() or len(message.strip()) != 2:
            return "❌ Invalid state code"

        state = message.strip().upper()
        session["step"] = AddCaseSteps.COURT

        courts:list[CourtItem] = await cases_service.get_courts(
            limit=10,
            search=None,
            state_code=state,
            court_type_code=None,)
        session["courts"] = courts

        return format_court_selection(courts)

    # 2️⃣ COURT
    elif step == AddCaseSteps.COURT:
        courts:list[CourtItem] = session.get("courts", [])
        court = map_input_to_court(message, session.get("courts", []))

        if not court:
            return "❌ Invalid selection. Enter valid number"

        data["court_code"] = court.court_code
        session["step"] = AddCaseSteps.PETITIONER

        return "👤 Enter Petitioner Name"

    # 3️⃣ PETITIONER
    elif step == AddCaseSteps.PETITIONER:
        if not message.strip():
            return "❌ Petitioner is required"

        data["petitioner"] = message.strip()
        session["step"] = AddCaseSteps.RESPONDENT

        return "👤 Enter Respondent Name"

    # 4️⃣ RESPONDENT
    elif step == AddCaseSteps.RESPONDENT:
        if not message.strip():
            return "❌ Respondent is required"

        data["respondent"] = message.strip()
        session["step"] = AddCaseSteps.NEXT_HEARING_DATE

        return "📅 Enter Next Hearing Date (DD-MM-YYYY) or type SKIP"

    # 5️⃣ DATE
    elif step == AddCaseSteps.NEXT_HEARING_DATE:
        if message.lower() != "skip":
            try:
                data["next_hearing_date"] = parse_date(message)
            except:
                return "❌ Invalid date format. Use DD-MM-YYYY or type SKIP"

        session["step"] = AddCaseSteps.CONFIRM
        return format_confirmation(data)

    # 6️⃣ CONFIRM
    elif step == AddCaseSteps.CONFIRM:
        if message.lower() not in ["yes", "y"]:
            clear(phone)
            return "❌ Cancelled"

        # 🔥 CALL YOUR SERVICE
        payload:CaseCreate=CaseCreate(**data)
        payload.status_code = RefmCaseStatusConstants.ACTIVE

        case = await cases_service.cases_add(            
            payload=payload
        )

        clear(phone)

        return f"""✅ Case Created


"""