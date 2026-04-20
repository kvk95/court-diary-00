import asyncio
from collections import defaultdict
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, union_all

from app.database.models.base.session import get_session
from app.database.models.case_aors import CaseAors
from app.database.models.cases import Cases
from app.database.models.chamber_roles import ChamberRoles
from app.database.models.hearings import Hearings
from app.database.models.refm_courts import RefmCourts
from app.database.models.user_chamber_link import UserChamberLink
from app.database.models.user_roles import UserRoles
from app.database.models.users import Users

from app.utils.email_util import EmailUtil
from app.utils.logging_framework.exception_logger import log_exception

# -----------------------------------------------------------------------------
# Scheduler
# -----------------------------------------------------------------------------
scheduler = AsyncIOScheduler()

def start_scheduler(job_fn):

    scheduler.add_job(
        job_fn,
        CronTrigger(hour=20, minute=0, timezone="Asia/Kolkata"),
        id="send_tomorrow_hearings",
        replace_existing=True,
    )
    scheduler.start()
    print("✅ Scheduler started (8 PM job registered)")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_tomorrow():
    return date.today() + timedelta(days=1)


# -----------------------------------------------------------------------------
# MAIN JOB
# -----------------------------------------------------------------------------
async def send_tomorrow_hearings_job():

    async for session in get_session():
        email_util = EmailUtil(session=session)

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


# -----------------------------------------------------------------------------
# QUERY
# -----------------------------------------------------------------------------
async def get_tomorrow_hearings(session):
    tomorrow = get_tomorrow()

    # -----------------------------
    # 1. AOR USERS
    # -----------------------------
    aor_stmt = (
        select(
            Cases.case_id,
            Cases.case_number,
            Cases.petitioner,
            Cases.respondent,
            Hearings.hearing_date,
            RefmCourts.court_name,
            Users.email,
            Users.first_name,
            Users.last_name,
        )
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(RefmCourts, RefmCourts.court_id == Cases.court_id)
        .join(CaseAors, CaseAors.case_id == Cases.case_id)
        .join(Users, Users.user_id == CaseAors.user_id)
        .where(
            Hearings.hearing_date == tomorrow,
            Cases.deleted_ind.is_(False),
        )
    )

    # -----------------------------
    # 2. ADMIN / SENIOR USERS
    # -----------------------------
    admin_stmt = (
        select(
            Cases.case_id,
            Cases.case_number,
            Cases.petitioner,
            Cases.respondent,
            Hearings.hearing_date,
            RefmCourts.court_name,
            Users.email,
            Users.first_name,
            Users.last_name,
        )
        .join(Hearings, Hearings.case_id == Cases.case_id)
        .join(RefmCourts, RefmCourts.court_id == Cases.court_id)
        .join(UserChamberLink, UserChamberLink.chamber_id == Cases.chamber_id)
        .join(UserRoles, UserRoles.link_id == UserChamberLink.link_id)
        .join(ChamberRoles, ChamberRoles.role_id == UserRoles.role_id)
        .join(Users, Users.user_id == UserChamberLink.user_id)
        .where(
            Hearings.hearing_date == tomorrow,
            Cases.deleted_ind.is_(False),
            ChamberRoles.role_code.in_(["ADMIN", "ASSO", "CNSL"]),
        )
    )

    # -----------------------------
    # UNION
    # -----------------------------
    stmt = union_all(aor_stmt, admin_stmt)

    result = await session.execute(stmt)
    return result.fetchall()


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
            "hearing_time": r.hearing_time,
        }

    return {
        email: list(cases.values())
        for email, cases in grouped.items()
    }


# -----------------------------------------------------------------------------
# EMAIL SENDER
# -----------------------------------------------------------------------------
semaphore = asyncio.Semaphore(10)

async def safe_send(email_util, email, hearings):
    async with semaphore:
        await send_hearing_email(email_util, email, hearings)

async def send_hearing_email(email_util, email, hearings):
    try:
        # 🔥 build table rows
        rows_html = ""
        for i, h in enumerate(hearings, start=1):
            rows_html += f"""
            <tr>
                <td>{i}</td>
                <td>{h['case_number']}</td>
                <td>{h['title']}</td>
                <td>{h['court_name']}</td>
                <td>{h['hearing_time'] or '-'}</td>
            </tr>
            """

        body = f"""
        <div style="font-family:Arial">

            <h2>📜 Cause List - Tomorrow</h2>

            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse:collapse;width:100%">
                <tr style="background:#7C3AED;color:white">
                    <th>#</th>
                    <th>Case No</th>
                    <th>Parties</th>
                    <th>Court</th>
                    <th>Time</th>
                </tr>
                {rows_html}
            </table>

            <p style="margin-top:20px;color:#777;">
                Generated by Court Diary System
            </p>

        </div>
        """

        email_util.send_email(
            to_emails=[email],
            subject=f"Tomorrow Hearings ({len(hearings)} Cases)",
            body=body,
        )

    except Exception as e:
        await log_exception(e)