# app/startup/scheduler.py

import asyncio
from datetime import date, datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database.models.base.session import get_session

from app.services.notification_service import NotificationService
from app.utils.email_util import EmailUtil

scheduler = AsyncIOScheduler()
notification_queue = asyncio.Queue()

WORKER_COUNT = 5
semaphore = asyncio.Semaphore(10)


# --------------------------------------------------
# START
# --------------------------------------------------
def start_scheduler():

    scheduler.add_job(
        enqueue_summary_job,
        CronTrigger(hour=20, minute=0),
    )

    scheduler.add_job(
        enqueue_reminder_job,
        CronTrigger(minute="*/5"),
    )

    scheduler.start()

    for _ in range(WORKER_COUNT):
        asyncio.create_task(queue_worker())


# --------------------------------------------------
# QUEUE WORKER
# --------------------------------------------------
async def queue_worker():
    while True:
        job = await notification_queue.get()

        try:
            await process_notification(job)
        finally:
            notification_queue.task_done()


# --------------------------------------------------
# ENQUEUE SUMMARY
# --------------------------------------------------
async def enqueue_summary_job():
    async for session in get_session():

        service = NotificationService(session=session)
        users = await service.get_users_settings(session)

        today = date.today()

        for u in users:

            if not u.email_enabled_ind:
                continue

            freq = u.email_summary_frequency_code

            if freq == "SFNN":
                continue

            if freq == "SFDL":
                start = today
                end = today
            elif freq == "SFWK":
                start = today
                end = today + timedelta(days=7)
            else:
                continue

            await notification_queue.put({
                "type": "SUMMARY",
                "user": u,
                "start": start,
                "end": end,
            })


# --------------------------------------------------
# ENQUEUE REMINDER
# --------------------------------------------------
async def enqueue_reminder_job():
    async for session in get_session():        

        service = NotificationService(session=session)
        users = await service.get_users_settings(session)

        now = datetime.now()

        for u in users:

            if not u.email_enabled_ind:
                continue

            remind_before = u.email_remind_before or 30

            await notification_queue.put({
                "type": "REMINDER",
                "user": u,
                "target_time": now + timedelta(minutes=remind_before),
            })


# --------------------------------------------------
# PROCESS
# --------------------------------------------------
async def process_notification(job):
    async with semaphore:
        async for session in get_session():

            service = NotificationService(session=session)
            email_util = EmailUtil(session=session)

            if job["type"] == "SUMMARY":
                await service.process_summary(email_util, job)

            elif job["type"] == "REMINDER":
                await service.process_reminder(email_util, job)