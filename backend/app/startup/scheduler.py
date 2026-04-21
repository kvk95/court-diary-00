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
    
    _logger.info(f"✅ Scheduler started (8 PM job registered)")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_tomorrow():
    return date.today() + timedelta(days=1)


# -----------------------------------------------------------------------------
# MAIN JOB
# -----------------------------------------------------------------------------
async def send_tomorrow_hearings_job():

    try:

        async for session in get_session():
            email_util:EmailUtil = EmailUtil(session=session)

            rows = await get_tomorrow_hearings(session)

            if not rows:
                return

            grouped = group_hearings_by_user(rows)

            tasks = [
                safe_send(email_util, email, hearings)
                    for email, hearings in grouped.items()
            ]

            # 🚀 parallel execution
            await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        await log_exception(e)


# -----------------------------------------------------------------------------
# QUERY
# -----------------------------------------------------------------------------
from sqlalchemy import select, union_all

async def get_tomorrow_hearings(session):

    tomorrow = get_tomorrow()

    # ---------------- AOR ----------------
    aor_stmt = (
        select(
            Cases.case_id,
            Cases.case_number,
            Cases.petitioner,
            Cases.respondent,
            Hearings.hearing_date,
            Courts.court_name,
            Users.email,
            Users.first_name,
            Users.last_name,
        )
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(Courts, Courts.court_code == Cases.court_code)
        .join(CaseAors, CaseAors.case_id == Cases.case_id)
        .join(Users, Users.user_id == CaseAors.user_id)
        .where(Hearings.hearing_date == tomorrow)
    )

    # ---------------- ADMIN ----------------
    admin_stmt = (
        select(
            Cases.case_id,
            Cases.case_number,
            Cases.petitioner,
            Cases.respondent,
            Hearings.hearing_date,
            Courts.court_name,
            Users.email,
            Users.first_name,
            Users.last_name,
        )
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

    # ---------------- UNION ----------------
    stmt = union_all(aor_stmt, admin_stmt)

    result = await session.execute(stmt)
    rows = result.fetchall()

    return rows


# -----------------------------------------------------------------------------
# GROUPING (ONE MAIL PER USER)
# -----------------------------------------------------------------------------
def group_hearings_by_user(rows):
    grouped = defaultdict(dict)

    for r in rows:
        email = r.email

        grouped[email][r.case_id] = {
            "case_number": r.case_number,
            "title": f"{r.petitioner} vs {r.respondent}",
            "court_name": r.court_name,
            "hearing_date": r.hearing_date,
            # "hearing_time": r.hearing_time,
        }

    return {
        email: list(cases.values())
        for email, cases in grouped.items()
    }


# -----------------------------------------------------------------------------
# EMAIL SENDER
# -----------------------------------------------------------------------------
semaphore = asyncio.Semaphore(10)

async def safe_send(email_util:EmailUtil, email, hearings):
    async with semaphore:
        await send_hearing_email(email_util, email, hearings)

async def send_hearing_email(email_util:EmailUtil, email, hearings):
    try:
        # 🔥 build table rows
        email = "kvk9540@gmail.com"
        await asyncio.to_thread(
            email_util.send_email,
            [email],
            "Tomorrow Hearings",
            build_body(hearings),
        )

    except Exception as e:
        _logger.info(f"sending mail to exception {e}")
        await log_exception(e)

def build_body(hearings):
    rows_html = ""
    for i, h in enumerate(hearings, start=1):
        rows_html += f"""
            <tr>
                <td style="padding:10px;border:1px solid #ddd;color:#000;">{i}</td>
                <td style="padding:10px;border:1px solid #ddd;color:#000;">{h['case_number']}</td>
                <td style="padding:10px;border:1px solid #ddd;color:#000;">{h['title']}</td>
                <td style="padding:10px;border:1px solid #ddd;color:#000;">{h['court_name']}</td>
            </tr>
            """

    body = f"""
        <div style="font-family:Arial, sans-serif; color:#000;">
            <h2 style="margin-bottom:5px; color:#000;">
                Tomorrow’s Hearings
            </h2>
            <table width="100%" cellpadding="0" cellspacing="0" 
                style="border-collapse:collapse; background:#ffffff;">
                <tr style="background:#7C3AED;">
                    <th style="padding:10px;border:1px solid #ddd;color:#ffffff;">#</th>
                    <th style="padding:10px;border:1px solid #ddd;color:#ffffff;">Case No</th>
                    <th style="padding:10px;border:1px solid #ddd;color:#ffffff;">Parties</th>
                    <th style="padding:10px;border:1px solid #ddd;color:#ffffff;">Court</th>
                </tr>
                {rows_html}
            </table>
            <p style="margin-top:20px;font-size:12px;color:#555;">
                This is an automated notification from Court Diary.
            </p>
        </div>
        """
    
    return body