# app\utils\logging_framework\audit_queue.py

import asyncio

from app.core.config import Settings


audit_queue: asyncio.Queue = asyncio.Queue(maxsize=Settings().LOGGING.LOG_QUEUE_MAXSIZE)