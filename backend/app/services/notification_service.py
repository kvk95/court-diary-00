# app/services/notification_service.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from datetime import datetime
import logging
from typing import Optional

from app.core.config import settings
from app.database.repositories.notification_log_repository import NotificationRepository
from app.services.base.base_service import BaseService
from app.dtos.scheduler_dto import NotificationLogCreate
from app.utils.logging_framework.exception_logger import log_exception

# -----------------------------------------------------------------------------
# LOGGER
# -----------------------------------------------------------------------------
_logger = logging.getLogger(__name__)

class NotificationService(BaseService):

    ADMIN_ROLES = {"ADMIN", "CNSL"}

    def __init__(self, 
        session: AsyncSession,
        repo: Optional[NotificationRepository] = None
    ):

        super().__init__(session)
        self.repo = repo or NotificationRepository()
        self.purpose_map = None
        self.status_map = None

    async def _load_maps(self):
        if self.purpose_map and self.status_map:
            return self.purpose_map, self.status_map
        
        self.purpose_map, self.status_map = await self.repo.get_refm_maps(self.session)
        return self.purpose_map, self.status_map

    # 🔹 Dedup insert
    async def log_notification(self, payload: NotificationLogCreate):
        # try:
        #     return await self.repo.create(
        #         session = self.session,
        #         data = payload.model_dump(exclude_unset=True, exclude_none=True)
        #     )
        # except IntegrityError:
        #     return None
        return 1
        
    async def get_users_settings(self, session):
        return await self.repo.get_users_settings(session = session)

    # =====================================================
    # SUMMARY
    # =====================================================
    async def process_summary(self, email_util, job):

        print(f"11111111111111111111111")
        rows = await self.repo.get_hearings_range(
            self.session, job["start"], job["end"]
        )
        
        print(f"rows 1 : {rows}")

        if not rows:
            return
        
        print(f"rows 2 : {rows}")

        purpose_map, status_map = await self._load_maps()

        grouped = self.group_hearings_by_user(rows)

        user = job["user"]

        hearings = (
            rows if user.role_code in self.ADMIN_ROLES
            else grouped.get(user.email, [])
        )
        
        print(f"rows 3 : {hearings}")

        if not hearings:
            return

        log = await self.log_notification(
            NotificationLogCreate(
                user_id=user.user_id,
                hearing_id=None,
                channel_code="EMAIL",
                type_code="SUMMARY",
                ref_date=job["start"],   # 🔥 IMPORTANT
                scheduled_at=datetime.now(),
            )
        )
        
        print(f"rows 4 : {log}")

        if not log:
            return

        body = build_body(hearings, purpose_map, status_map)

        await send_hearing_email(
            email_util,
            user.email,
            "Your Hearing Summary — NyaDesk",
            body
        )

    # =====================================================
    # REMINDER
    # =====================================================
    async def process_reminder(self, email_util, job):

        rows = await self.repo.get_hearings_for_reminder(
            self.session, job["target_time"]
        )

        if not rows:
            return

        purpose_map, status_map = await self._load_maps()

        grouped = self.group_hearings_by_user(rows)

        user = job["user"]

        hearings = (
            rows if user.role_code in self.ADMIN_ROLES
            else grouped.get(user.email, [])
        )

        if not hearings:
            return

        for h in hearings:

            log = await self.log_notification(
                NotificationLogCreate(
                    user_id=user.user_id,
                    hearing_id=h.hearing_id,
                    channel_code="EMAIL",
                    type_code="REMINDER",
                    scheduled_at=job["target_time"],
                )
            )

            if not log:
                continue

            body = build_body(
                hearings=[h],
                purpose_map=purpose_map,
                status_map=status_map,
                title="⏰ Upcoming Hearing Reminder",
                subtitle="You have upcoming hearings shortly:"
            )

            await send_hearing_email(
                email_util,
                user.email,
                "Upcoming Hearing Reminder — NyaDesk",
                body
            )

    # -----------------------------------------------------------------------------
    # GROUPING  (one email per user, deduplicated by hearing_id)
    # -----------------------------------------------------------------------------
    def group_hearings_by_user(self, rows) -> dict[str, list]:
        """
        Groups rows by recipient email.
        Deduplicates by hearing_id so AOR + admin overlap doesn't double-list.
        """
        grouped: dict[str, dict] = defaultdict(dict)

        for r in rows:
            grouped[r.email][r.hearing_id] = r

        return {
            email: list(hearings.values())
            for email, hearings in grouped.items()
        }



# -----------------------------------------------------------------------------
# EMAIL BODY
# -----------------------------------------------------------------------------

def format_date(d) -> str:
    """Format a date/datetime as  23 Apr 2026.  Returns '—' for None."""
    if d is None:
        return "—"
    try:
        # %d gives day with leading zero, so strip it
        return d.strftime("%d %b %Y").lstrip("0")
    except Exception as e:
        print(e)
        return str(d)

def badge(status_map, status_code):
    status_text = (status_map.get(status_code) or status_code or "").upper()

    if status_text == "UPCOMING":
        return "#dbeafe", "#1e40af", "Upcoming"
    elif status_text == "COMPLETED":
        return "#dcfce7", "#065f46", "Completed"
    elif status_text == "ADJOURNED":
        return "#fff7ed", "#92400e", "Adjourned"
    else:
        return "#e5e7eb", "#374151", status_text.title()

def build_summary(hearings, status_map):
    total = len(hearings)

    def get_status(code):
        return (status_map.get(code) or code or "").upper()

    upcoming = sum(1 for h in hearings if get_status(h.status_code) == "UPCOMING")
    completed = sum(1 for h in hearings if get_status(h.status_code) == "COMPLETED")
    adjourned = sum(1 for h in hearings if get_status(h.status_code) == "ADJOURNED")

    return total, upcoming, completed, adjourned

def build_table(
    hearings,
    purpose_map,
    status_map,
    ui_url,
    include_notes=True
):
    rows_html = ""

    for i, h in enumerate(hearings, start=1):

        case_link = f"{ui_url}/cases/{h.case_id}"

        court_name = h.court_name or "—"

        purpose_label = purpose_map.get(h.purpose_code, h.purpose_code or "—")

        badge_bg, badge_fg, status_label = badge(status_map, h.status_code)

        note_text = h.notes or "—"

        rows_html += f"""
        <tr style="background:{'#f9fafb' if i % 2 == 0 else '#ffffff'};">
            <td style="padding:10px;">{i}</td>

            <td style="padding:10px; white-space:nowrap;">
                <a href="{case_link}" style="color:#0ea5e9; text-decoration:none; font-weight:500;">
                    {h.case_number}
                </a>
            </td>

            <td style="padding:10px; line-height:1.4;">
                <b>{h.petitioner}</b> vs <b>{h.respondent}</b>
            </td>

            <td style="padding:10px;">
                {court_name}
            </td>

            <td style="padding:10px; white-space:nowrap;">
                {format_date(h.hearing_date)}
            </td>

            <td style="padding:10px;">
                {purpose_label}
            </td>

            <td style="padding:10px; white-space:nowrap;">
                <span style="
                    display:inline-block;
                    padding:6px 14px;
                    border-radius:20px;
                    font-size:12px;
                    font-weight:700;
                    min-width:90px;
                    text-align:center;
                    background:{badge_bg};
                    color:{badge_fg};
                ">
                    {status_label}
                </span>
            </td>

            <td style="padding:10px; white-space:nowrap;">
                <b>{format_date(h.next_hearing_date)}</b>
            </td>
        """

        if include_notes:
            rows_html += f"""
            <td style="padding:10px;">
                <div style="max-width:220px; word-wrap:break-word;">
                    <i>{note_text}</i>
                </div>
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
            table-layout:auto;
        ">
        <tr style="background:#2563eb; color:#e5e7eb;;">
            <th width="40">#</th>
            <th width="160" align="left">Case</th>
            <th width="200" align="left">Parties</th>
            <th width="120" align="left">Court</th>
            <th width="120" align="left">Date</th>
            <th width="140" align="left">Purpose</th>
            <th width="140" align="left">Status</th>
            <th width="140" align="left">Next</th>
            {notes_header}
        </tr>
        {rows_html}
    </table>
    """

def build_body(hearings, purpose_map, status_map, title=None, subtitle=None):
    ui_url = settings.UI_URL

    today_full = datetime.now().strftime("%A, %d %b %Y")
    today_short = datetime.now().strftime("%d %b %Y")

    total, upcoming, completed, adjourned = build_summary(hearings, status_map)

    table_html = build_table(
        hearings,
        purpose_map,
        status_map,
        ui_url,
        include_notes=True
    )

    cards_html = build_mobile_cards(
        hearings,
        purpose_map,
        status_map,
        ui_url
    )

    title = title or "NYADESK · AUTOMATED DIGEST"
    subtitle = subtitle or f"{total} hearings today"
    return f"""
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0; padding:0; background:#f3f4f6; font-family:'Inter', Arial, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="100%" cellpadding="0" cellspacing="0"
       style="max-width:1100px; background:#ffffff; border-radius:12px; overflow:hidden;">

    <!-- HEADER -->
    <tr>
        <td style="background:#0F172A; color:#fff; padding:20px;">
            <h2 style="margin:0;">{title}</h2>
            <p style="margin:6px 0 0;">Court diary update · {today_full}</p>
            <p style="margin:6px 0 0;">{subtitle}</p>
        </td>
    </tr>

    <!-- STATS -->
    <tr>
        <td style="padding:20px;">
            <table width="100%" style="table-layout:fixed;">
                <tr>
                    <td align="center" style="background:#1E3A8A; color:#fff; padding:12px; border-radius:8px;">
                        TOTAL<br><b>{total}</b>
                    </td>
                    <td align="center" style="background:#dbeafe; color:#1e40af; padding:12px; border-radius:8px;">
                        UPCOMING<br><b>{upcoming}</b>
                    </td>
                    <td align="center" style="background:#dcfce7; color:#065f46; padding:12px; border-radius:8px;">
                        COMPLETED<br><b>{completed}</b>
                    </td>
                    <td align="center" style="background:#fff7ed; color:#92400e; padding:12px; border-radius:8px;">
                        ADJOURNED<br><b>{adjourned}</b>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- TABLE -->
    <tr>
        <td style="padding:20px;">
            <h3 style="margin:0 0 10px 0;">Hearing Schedule · {today_short}</h3>
            {table_html}
        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td style="padding:20px; font-size:12px; color:#6b7280;">
            Automated email from NyaDesk
        </td>
    </tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""



    # <!-- MOBILE CARDS -->
    # <tr class="mobile-cards">
    #     <td style="padding:10px;">
    #         {cards_html}
    #     </td>
    # </tr>

def build_mobile_cards(hearings, purpose_map, status_map, ui_url):
    cards = ""

    for h in hearings:
        case_link = f"{ui_url}/cases/{h.case_id}"

        badge_bg, badge_fg, status_label = badge(status_map, h.status_code)

        cards += f"""
        <div style="background:#ffffff; border-radius:10px; padding:12px; margin-bottom:10px; border:1px solid #e5e7eb;">
            
            <a href="{case_link}" style="color:#0ea5e9; font-weight:bold; text-decoration:none;">
                {h.case_number}
            </a>

            <div style="margin-top:6px; font-size:13px;">
                {h.petitioner} vs {h.respondent}
            </div>

            <div style="margin-top:6px; font-size:12px; color:#555;">
                {h.court_name or "—"}
            </div>

            <div style="margin-top:6px; font-size:12px;">
                📅 {format_date(h.hearing_date)}
            </div>

            <div style="margin-top:6px;">
                <span style="
                    display:inline-block;
                    padding:5px 10px;
                    border-radius:20px;
                    font-size:11px;
                    background:{badge_bg};
                    color:{badge_fg};
                ">
                    {status_label}
                </span>
            </div>

        </div>
        """

    return cards

async def send_hearing_email(
    email_util,
    email,
    subject,
    body
):
    try:
        # ? REMOVE this (bug)
        email = "kvk9540@gmail.com"

        await asyncio.to_thread(
            email_util.send_email,
            to_emails =[email],
            subject = subject,
            body = body,
            attach_body = False
        )
    except Exception as e:
        _logger.error(f"Failed to send email to {email}: {e}")
        print(e)        
        await log_exception(e)

# -----------------------------------------------------------------------------
# TODO FUTURE CHANNELS
# -----------------------------------------------------------------------------
# TODO: SMS Integration
# TODO: WhatsApp Integration