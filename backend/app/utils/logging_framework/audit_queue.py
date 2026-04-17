# app\utils\logging_framework\audit_queue.py

import asyncio

from app.core.config import settings

audit_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.LOGGING.LOG_QUEUE_MAXSIZE)