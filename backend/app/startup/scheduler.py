import asyncio
from collections import defaultdict
from datetime import date, timedelta
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func, select, union_all

from app.database.models.base.session import get_session
from app.database.models.case_aors import CaseAors
from app.database.models.case_notes import CaseNotes
from app.database.models.cases import Cases
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.courts import Courts
from app.database.models.hearings import Hearings
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_hearing_status import RefmHearingStatus
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users

from app.utils.email_util import EmailUtil
from app.utils.logging_framework.exception_logger import log_exception

# -----------------------------------------------------------------------------
# Scheduler
# -----------------------------------------------------------------------------
scheduler = AsyncIOScheduler()
_logger = logging.getLogger(__name__)


def start_scheduler(job_fn):
    scheduler.add_job(
        job_fn,
        CronTrigger(hour=20, minute=0, timezone="Asia/Kolkata"),
        id="send_tomorrow_hearings",
        replace_existing=True,
    )
    scheduler.start()
    _logger.info("? Scheduler started (8 PM IST job registered)")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_tomorrow() -> date:
    return date.today() + timedelta(days=1)


def format_date(d) -> str:
    """Format a date/datetime as  23 Apr 2026.  Returns '—' for None."""
    if d is None:
        return "—"
    try:
        return d.strftime("%-d %b %Y")
    except Exception:
        return str(d)


# -----------------------------------------------------------------------------
# MAIN JOB
# -----------------------------------------------------------------------------
async def send_tomorrow_hearings_job():
    try:
        async for session in get_session():
            email_util: EmailUtil = EmailUtil(session=session)

            rows_tomorrow  = await get_tomorrow_hearings(session)
            rows_today = await get_today_hearings_with_notes(session)
            
            if not rows_tomorrow :
                _logger.info("No hearings tomorrow — skipping email job.")
                return
            
            print(len(rows_tomorrow ))

            purpose_map, status_map = await get_refm_maps(session)
            grouped_tomorrow = group_hearings_by_user(rows_tomorrow)
            grouped_today = group_hearings_by_user(rows_today)

            tasks = [
                safe_send(
                    email_util,
                    email,
                    grouped_today.get(email, []),
                    grouped_tomorrow.get(email, []),
                    purpose_map,
                    status_map
                )
                for email in grouped_tomorrow.keys() | grouped_today.keys()
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        print(e)
        await log_exception(e)


# -----------------------------------------------------------------------------
# QUERY
# -----------------------------------------------------------------------------
_HEARING_COLS = [
    Cases.case_id,
    Cases.case_number,
    Cases.petitioner,
    Cases.respondent,
    Hearings.hearing_id,
    Hearings.hearing_date,
    Hearings.purpose_code,
    Hearings.status_code,
    Hearings.next_hearing_date,
    Hearings.notes,
    Courts.court_name,
    Users.email,
    Users.first_name,
    Users.last_name,
]


async def get_tomorrow_hearings(session):
    tomorrow = get_tomorrow()

    # -- AOR ------------------------------------------------------------------
    aor_stmt = (
        select(*_HEARING_COLS)
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .join(CaseAors, CaseAors.case_id == Cases.case_id)
        .join(Users, Users.user_id == CaseAors.user_id)
        .where(Hearings.hearing_date == tomorrow)
    )

    # -- ADMIN / ASSO / CNSL --------------------------------------------------
    admin_stmt = (
        select(*_HEARING_COLS)
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .join(UserChamberLink, UserChamberLink.chamber_id == Cases.chamber_id)
        .join(UserRoles, UserRoles.link_id == UserChamberLink.link_id)
        .join(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
        .join(Users, Users.user_id == UserChamberLink.user_id)
        .where(
            Hearings.hearing_date == tomorrow,
            ChamberRoles.role_code.in_(["ADMIN", "ASSO", "CNSL"]),
        )
    )

    combined = union_all(aor_stmt, admin_stmt).subquery()

    stmt = select(*combined.c).distinct(
        combined.c.hearing_id,
        combined.c.email
    ).order_by(combined.c.hearing_date)

    result = await session.execute(stmt)
    return result.mappings().all()

async def get_today_hearings_with_notes(session):
    today = date.today()

    latest_note_subq = (
        select(
            CaseNotes.case_id,
            func.max(CaseNotes.created_date).label("max_date")
        )
        .where(
            CaseNotes.deleted_ind == False,
            CaseNotes.private_ind == False
        )
        .group_by(CaseNotes.case_id)
        .subquery()
    )

    notes_join = (
        select(CaseNotes.case_id, CaseNotes.note_text)
        .join(
            latest_note_subq,
            (CaseNotes.case_id == latest_note_subq.c.case_id) &
            (CaseNotes.created_date == latest_note_subq.c.max_date)
        )
        .subquery()
    )

    stmt = (
        select(*_HEARING_COLS, notes_join.c.note_text)
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .outerjoin(notes_join, notes_join.c.case_id == Cases.case_id)
        .where(Hearings.hearing_date == today)
    )

    result = await session.execute(stmt)
    return result.mappings().all()


# -----------------------------------------------------------------------------
# REFERENCE MAP  (purpose & status code ? description)
# -----------------------------------------------------------------------------
async def get_refm_maps(session) -> tuple[dict, dict]:
    purpose_rows = await session.execute(
        select(RefmHearingPurpose.code, RefmHearingPurpose.description)
    )
    status_rows = await session.execute(
        select(RefmHearingStatus.code, RefmHearingStatus.description)
    )
    purpose_map = {r.code: r.description for r in purpose_rows}
    status_map  = {r.code:  r.description  for r in status_rows}
    return purpose_map, status_map


# -----------------------------------------------------------------------------
# GROUPING  (one email per user, deduplicated by hearing_id)
# -----------------------------------------------------------------------------
def group_hearings_by_user(rows) -> dict[str, list]:
    """
    Groups rows by recipient email.
    Deduplicates by hearing_id so AOR + admin overlap doesn't double-list.
    """
    grouped: dict[str, dict] = defaultdict(dict)

    for r in rows:
        grouped[r["email"]][r["hearing_id"]] = r

    return {
        email: list(hearings.values())
        for email, hearings in grouped.items()
    }


# -----------------------------------------------------------------------------
# EMAIL SENDER
# -----------------------------------------------------------------------------
semaphore = asyncio.Semaphore(10)


async def safe_send(
    email_util: EmailUtil,
    email: str,
    today_hearings: list,
    tomorrow_hearings: list,
    purpose_map: dict,
    status_map: dict
):
    async with semaphore:
        await send_hearing_email(
            email_util,
            email,
            today_hearings,
            tomorrow_hearings,
            purpose_map,
            status_map
        )


async def send_hearing_email(
    email_util,
    email,
    today_hearings,
    tomorrow_hearings,
    purpose_map,
    status_map
):
    try:
        # ? REMOVE this (bug)
        email = "kvk9540@gmail.com"

        await asyncio.to_thread(
            email_util.send_email,
            [email],
            "Today's Summary & Tomorrow's Hearings — NyaDesk",
            build_body(
                today_hearings,
                tomorrow_hearings,
                purpose_map,
                status_map
            ),
        )
    except Exception as e:
        _logger.error(f"Failed to send email to {email}: {e}")
        await log_exception(e)


# -----------------------------------------------------------------------------
# EMAIL BODY
# -----------------------------------------------------------------------------
_STATUS_BADGE = {
    "UPCOMING":  ("#eff6ff", "#3b82f6"),
    "COMPLETED": ("#f0fdf4", "#16a34a"),
    "ADJOURNED": ("#fff7ed", "#f97316"),
    "DISMISSED": ("#fef2f2", "#ef4444"),
}

def build_summary(hearings):
    total = len(hearings)
    status_count = defaultdict(int)

    for h in hearings:
        status_count[h.status_code] += 1

    return total, status_count

def build_table(
    hearings,
    purpose_map,
    status_map,
    ui_url,
    include_notes=False
):
    rows_html = ""

    for i, h in enumerate(hearings, start=1):
        case_link = f"{ui_url}cases/{h.case_id}"

        case_number = h.case_number
        parties = f"{h.petitioner} vs {h.respondent}"
        court_name = h.court_name or "—"
        hearing_date = format_date(h.hearing_date)

        purpose_label = purpose_map.get(h.purpose_code, h.purpose_code or "—")
        status_label = status_map.get(h.status_code, h.status_code or "—")

        next_date = format_date(h.next_hearing_date)

        note_text = getattr(h, "note_text", None)
        if note_text:
            note_text = (note_text[:120] + "...") if len(note_text) > 120 else note_text
        else:
            note_text = "—"

        row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"

        badge_bg, badge_fg = _STATUS_BADGE.get(
            (h.status_code or "").upper(),
            ("#f1f5f9", "#64748b")
        )

        rows_html += f"""
        <tr style="background:{row_bg};">

            <td style="padding:10px;">{i}</td>

            <td style="padding:10px;">
                <a href="{case_link}" style="color:#0ea5e9; text-decoration:none;">
                    {case_number}
                </a>
            </td>

            <td style="padding:10px;">{parties}</td>
            <td style="padding:10px;">{court_name}</td>
            <td style="padding:10px;">{hearing_date}</td>
            <td style="padding:10px;">{purpose_label}</td>

            <td style="padding:10px;">
                <span style="color:{badge_fg}; background:{badge_bg};
                             padding:3px 8px; border-radius:6px;">
                    {status_label}
                </span>
            </td>

            <td style="padding:10px;">{next_date}</td>
        """

        if include_notes:
            rows_html += f"""
            <td style="padding:10px; max-width:220px;">
                {note_text}
            </td>
            """

        rows_html += "</tr>"

    notes_header = "<th>Notes</th>" if include_notes else ""

    return f"""
    <table width="100%" style="border-collapse:collapse; margin-top:10px;">
        <tr style="background:#0f172a; color:#fff;">
            <th>#</th>
            <th>Case</th>
            <th>Parties</th>
            <th>Court</th>
            <th>Date</th>
            <th>Purpose</th>
            <th>Status</th>
            <th>Next</th>
            {notes_header}
        </tr>
        {rows_html}
    </table>
    """

def build_table(
    hearings,
    purpose_map,
    status_map,
    ui_url,
    include_notes=False
):
    rows_html = ""

    for i, h in enumerate(hearings, start=1):
        case_link = f"{ui_url}cases/{h.case_id}"

        parties = f"{h.petitioner} vs {h.respondent}"
        court_name = h.court_name or "—"

        purpose_label = purpose_map.get(h.purpose_code, h.purpose_code or "—")
        status_label = status_map.get(h.status_code, h.status_code or "—")

        note_text = getattr(h, "note_text", None) or "—"
        if note_text != "—":
            note_text = note_text[:100] + "..." if len(note_text) > 100 else note_text

        badge_bg, badge_fg = _STATUS_BADGE.get(
            (h.status_code or "").upper(),
            ("#eef2f7", "#475569")
        )

        rows_html += f"""
        <tr>
            <td align="center" style="padding:10px; vertical-align:top;">{i}</td>

            <td style="padding:10px; vertical-align:top; white-space:nowrap;">
                <a href="{case_link}" style="color:#0ea5e9; text-decoration:none; font-weight:500;">
                    {h.case_number}
                </a>
            </td>

            <td style="padding:10px; vertical-align:top; line-height:1.4;">
                {parties}
            </td>

            <td style="padding:10px; vertical-align:top; line-height:1.4;">
                {court_name}
            </td>

            <td style="padding:10px; vertical-align:top; white-space:nowrap;">
                {format_date(h.hearing_date)}
            </td>

            <td style="padding:10px; vertical-align:top;">
                {purpose_label}
            </td>

            <td style="padding:10px; vertical-align:top;">
                <span style="
                    display:inline-block;
                    padding:4px 8px;
                    border-radius:6px;
                    font-size:11px;
                    font-weight:600;
                    background:{badge_bg};
                    color:{badge_fg};
                    white-space:nowrap;">
                    {status_label}
                </span>
            </td>

            <td style="padding:10px; vertical-align:top; white-space:nowrap;">
                {format_date(h.next_hearing_date)}
            </td>
        """

        if include_notes:
            rows_html += f"""
            <td style="padding:10px; vertical-align:top; line-height:1.4; max-width:220px;">
                {note_text}
            </td>
            """

        rows_html += "</tr>"
    
    notes_header = "<th align='left'>Notes</th>" if include_notes else ""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
        style="
            border-collapse:collapse;
            width:100%;
            font-size:13px;
            table-layout:fixed;
        ">

        <tr style="background:#0f172a; color:#ffffff;">
            <th width="40">#</th>
            <th width="140" align="left">Case</th>
            <th align="left">Parties</th>
            <th width="160" align="left">Court</th>
            <th width="110" align="left">Date</th>
            <th width="120" align="left">Purpose</th>
            <th width="110" align="left">Status</th>
            <th width="110" align="left">Next</th>
            {notes_header}
        </tr>

        {rows_html}

    </table>
    """