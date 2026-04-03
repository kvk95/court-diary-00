import asyncio
import logging
from typing import Optional, cast

from app.core.config import settings
from .file_writer import FileWriter
from .logging_repo import LoggingRepo
from .log_types import LogType

_logger = logging.getLogger(__name__)


class LoggingQueueManager:
    def __init__(self):
        logging_cfg = settings.LOGGING

        self.queue = asyncio.Queue(maxsize=logging_cfg.LOG_QUEUE_MAXSIZE)
        self.workers = []
        self.repo: LoggingRepo
        self.file_writer = FileWriter(logging_cfg)
        self._started = False
        self._logging_cfg = logging_cfg

    async def start(self):
        if self._started:
            return

        self.repo = LoggingRepo(self._logging_cfg)

        for _ in range(self._logging_cfg.LOG_WORKER_COUNT):
            self.workers.append(asyncio.create_task(self._worker()))

        self._started = True

    async def stop(self):
        for _ in self.workers:
            await self.queue.put(None)

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        self._started = False

    async def enqueue(self, log_type: LogType, payload: dict):
        """
        Enqueue a log item with a LogType enum and payload.
        """
        item = {"type": log_type, "payload": payload}
        try:
            await self.queue.put(item)
        except asyncio.QueueFull:
            _logger.warning("Queue full. Dropping log item.")

    async def _worker(self):
        while True:
            item = await self.queue.get()
            if item is None:
                break
            try:
                await self._process(item)
            except Exception:
                _logger.exception("Failed processing log item")
            finally:
                self.queue.task_done()

    def pretty_log_payload(
        self, payload: dict, log_type: LogType, format_output: bool = False
    ):
        lines = []
        lines.append(
            f"\n****** {log_type} :: request id {payload.get('request_id')} ******\n"
        )

        if log_type == LogType.HTTP_LOG:
            lines.append("🌐 [HTTP Request]")
            lines.append(f"   ⤷  Method       : {payload.get('method')}")
            lines.append(f"   ⤷  Path         : {payload.get('path')}")
            lines.append(f"   ⤷  Status Code  : {payload.get('status_code')}")
            lines.append(f"   ⤷  Duration     : {payload.get('duration_ms')} ms")
            lines.append(f"   ⤷  Timestamp    : {payload.get('timestamp')}")
            lines.append(f"   ⤷  IP Address   : {payload.get('ip')}")
            lines.append(f"   ⤷  User ID      : {payload.get('user_id')}")
            lines.append(f"   ⤷  Company ID   : {payload.get('company_id')}")
            lines.append("\n📥 [Input]")
            lines.append(f"   ⤷ [Query Params] : {payload.get('query_params')}")
            lines.append(f"   ⤷ [Path Params]  : {payload.get('path_params')}")
            lines.append(f"   ⤷ [Request Body] : {payload.get('request_body')}")
            lines.append("\n📥 [Output]")
            lines.append(f"   ⤷ [Content Ttype] : {payload.get('content_type')}")
            lines.append(f"   ⤷ [Response]: {payload.get('response_body')}")
            if payload.get("error"):
                lines.append(f"   ⤷ [Error]   : {payload.get('error')}")

        elif log_type == LogType.DB_CALL:
            lines.append("📦 [DB Query]")
            lines.append(f"   ⤷ Timestamp    : {payload.get('timestamp')}")
            lines.append(f"   ⤷ Duration     : {payload.get('duration_ms')} ms")
            lines.append(f"   ⤷ Repo         : {payload.get('repo')}")
            lines.append(f"   ⤷ User ID      : {payload.get('user_id')}")
            lines.append(f"   ⤷ Company ID   : {payload.get('company_id')}")
            lines.append(f"   ⤷ Error        : {payload.get('error')}")

            lines.append("\n[Raw Query]")
            lines.append(str(payload.get("raw_query")))

            lines.append("\n[Params]")
            lines.append(str(payload.get("params")))

            lines.append("\n[Final Query]")
            lines.append(str(payload.get("final_query")))

            lines.append("\n[Metadata]")
            lines.append(str(payload.get("metadataz")))

        else:
            if format_output:
                import json

                lines.append(
                    json.dumps(payload, indent=4, default=str, ensure_ascii=False)
                )
            else:
                lines.append(str(payload))

        # Join all lines and log once
        block = "\n".join(lines)
        _logger.info(block)

    async def _process(self, item: dict):
        log_type: LogType = cast(LogType, item["type"])
        payload = item["payload"]
        cfg = self._logging_cfg

        if log_type == LogType.HTTP_LOG:
            targets = cfg.LOG_REQ_RESP

            if cfg.log_to_file(targets):
                await self.file_writer.write_http(payload)

            if cfg.log_to_db(targets):
                # await self.repo.insert_http(payload)
                pass

            if cfg.log_to_console(targets):
                self.pretty_log_payload(payload=payload, log_type=log_type)

        elif log_type == LogType.DB_CALL:
            targets = cfg.LOG_DB_CALL

            if cfg.log_to_file(targets):
                await self.file_writer.write_db_call(payload)

            if cfg.log_to_db(targets):
                await self.repo.insert_db_call(payload)

            if cfg.log_to_console(targets):
                self.pretty_log_payload(payload=payload, log_type=log_type)

        elif log_type == LogType.EXCEPTION:
            targets = cfg.LOG_EXCEPTION

            if cfg.log_to_file(targets):
                await self.file_writer.write_exception(payload)

            # if cfg.log_to_db(targets):
            #     await self.repo.insert_exception(payload)

            if cfg.log_to_console(targets):
                self.pretty_log_payload(payload=payload, log_type=log_type)

        elif log_type == LogType.ACTIVITY:
            targets = cfg.LOG_ACTIVITY

            if cfg.log_to_file(targets):
                await self.file_writer.write_activity(payload)

            if cfg.log_to_db(targets):
                await self.repo.insert_activity(payload)

            if cfg.log_to_console(targets):
                self.pretty_log_payload(payload=payload, log_type=log_type)


_queue_manager: Optional[LoggingQueueManager] = None


def get_queue_manager() -> LoggingQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = LoggingQueueManager()
    return _queue_manager
