import asyncio
from collections import defaultdict
from datetime import date, timedelta
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, union_all

from app.database.models.base.session import get_session
from app.database.models.case_aors import CaseAors
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
    _logger.info("✅ Scheduler started (8 PM IST job registered)")


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

            rows = await get_tomorrow_hearings(session)
            if not rows:
                _logger.info("No hearings tomorrow — skipping email job.")
                return

            purpose_map, status_map = await get_refm_maps(session)
            grouped = group_hearings_by_user(rows)

            tasks = [
                safe_send(email_util, email, hearings, purpose_map, status_map)
                for email, hearings in grouped.items()
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

    # ── AOR ──────────────────────────────────────────────────────────────────
    aor_stmt = (
        select(*_HEARING_COLS)
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .join(CaseAors, CaseAors.case_id == Cases.case_id)
        .join(Users, Users.user_id == CaseAors.user_id)
        # .where(Hearings.hearing_date == tomorrow)
    )

    # ── ADMIN / ASSO / CNSL ──────────────────────────────────────────────────
    admin_stmt = (
        select(*_HEARING_COLS)
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .join(UserChamberLink, UserChamberLink.chamber_id == Cases.chamber_id)
        .join(UserRoles, UserRoles.link_id == UserChamberLink.link_id)
        .join(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
        .join(Users, Users.user_id == UserChamberLink.user_id)
        .where(
            # Hearings.hearing_date == tomorrow,
            ChamberRoles.role_code.in_(["ADMIN", "ASSO", "CNSL"]),
        )
    )

    result = await session.execute(union_all(aor_stmt, admin_stmt))
    return result.mappings().all()


# -----------------------------------------------------------------------------
# REFERENCE MAP  (purpose & status code → description)
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


async def safe_send(email_util: EmailUtil, email: str, hearings: list,
                    purpose_map: dict, status_map: dict):
    async with semaphore:
        await send_hearing_email(email_util, email, hearings, purpose_map, status_map)


async def send_hearing_email(email_util: EmailUtil, email: str, hearings: list,
                              purpose_map: dict, status_map: dict):
    try:
        email = "kvk9540@gmail.com"
        await asyncio.to_thread(
            email_util.send_email,
            [email],
            "Tomorrow's Hearings — NyaDesk",
            build_body(hearings, purpose_map, status_map),
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


def build_body(hearings, purpose_map: dict , status_map: dict) -> str:
    purpose_map = purpose_map or {}
    status_map  = status_map  or {}

    rows_html = ""
    for i, h in enumerate(hearings, start=1):
        case_number    = h.case_number
        parties        = f"{h.petitioner} vs {h.respondent}"
        court_name     = h.court_name or "—"
        hearing_date   = format_date(h.hearing_date)
        purpose_label  = purpose_map.get(h.purpose_code, h.purpose_code or "—")
        status_label   = status_map.get(h.status_code,  h.status_code  or "—")
        next_date      = format_date(h.next_hearing_date)
        row_bg         = "#ffffff" if i % 2 == 0 else "#f8fafc"

        badge_bg, badge_fg = _STATUS_BADGE.get(
            (h.status_code or "").upper(), ("#f1f5f9", "#64748b")
        )

        rows_html += f"""
            <tr style="background:{row_bg};">
                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#94a3b8; font-size:13px; text-align:center;
                            font-weight:500; width:36px;">{i}</td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;">
                    <span style="display:inline-block; font-size:12px; font-weight:600;
                                 color:#0ea5e9; background:#eff6ff;
                                 padding:3px 10px; border-radius:20px; white-space:nowrap;">
                        {case_number}
                    </span>
                </td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#1e293b; font-size:13px; font-weight:500;">{parties}</td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#475569; font-size:13px;">{court_name}</td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#475569; font-size:13px; white-space:nowrap;">{hearing_date}</td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#475569; font-size:13px;">{purpose_label}</td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;">
                    <span style="display:inline-block; font-size:11px; font-weight:600;
                                 color:{badge_fg}; background:{badge_bg};
                                 padding:3px 10px; border-radius:20px; white-space:nowrap;
                                 text-transform:uppercase; letter-spacing:0.3px;">
                        {status_label}
                    </span>
                </td>

                <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0;
                            color:#64748b; font-size:13px; white-space:nowrap;">{next_date}</td>
            </tr>
        """

    return f"""
        <div style="font-family:'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:#1e293b;">

            <div style="margin-bottom:24px;">
                <div style="display:inline-block; width:44px; height:44px;
                             background:linear-gradient(135deg,#e0f2fe,#bae6fd);
                             border-radius:10px; margin-bottom:14px;
                             text-align:center; line-height:44px; font-size:20px;">⚖️</div>
                <h2 style="margin:0 0 6px; font-size:20px; font-weight:700;
                            color:#0f172a; letter-spacing:-0.3px;">Tomorrow's Hearings</h2>
                <p style="margin:0; font-size:14px; color:#64748b;">
                    Here's a full summary of your scheduled hearings. Please review and prepare accordingly.
                </p>
            </div>

            <div style="overflow-x:auto;">
                <table width="100%" cellpadding="0" cellspacing="0"
                    style="border-collapse:collapse; border:1px solid #e2e8f0;
                           border-radius:10px; overflow:hidden; font-size:14px; min-width:640px;">

                    <tr style="background:#0f172a;">
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:center; width:36px;">#</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Case No.</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Parties</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Court</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Date</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Purpose</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Status</th>
                        <th style="padding:11px 16px; color:#94a3b8; font-size:10px; font-weight:600;
                                   text-transform:uppercase; letter-spacing:0.6px; text-align:left;">Next Date</th>
                    </tr>

                    {rows_html}
                </table>
            </div>

            <div style="text-align:center; margin:28px 0 8px;">
                <a href="https://court-diary.nyainfo.com/calendar"
                    style="display:inline-block; background:#0ea5e9; color:#ffffff;
                           font-size:14px; font-weight:600; padding:13px 28px;
                           border-radius:10px; text-decoration:none; letter-spacing:0.1px;">
                    View Full Calendar →
                </a>
            </div>

            <p style="margin-top:20px; font-size:12px; color:#94a3b8; text-align:center;
                       border-top:1px solid #f1f5f9; padding-top:16px;">
                This is an automated notification from NyaDesk. Please do not reply to this email.
            </p>
        </div>
    """