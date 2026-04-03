from datetime import datetime

from app.utils.logging_framework.schemas import ActivityLogPayload, ActivityMetadata

from .log_types import LogType
from .logging_util import add_to_queue

async def log_activity(
    action: str,
    target: str | None = None,
    metadata: dict | None = None,
):
    activity_payload = ActivityLogPayload(
        action=action,
        target=target,
        metadata_json=ActivityMetadata(**metadata) if metadata else None,
        timestamp=datetime.utcnow(),
    )

    await add_to_queue(
        log_type=LogType.ACTIVITY,
        payload=activity_payload.model_dump(mode="json")  # ✅ important
    )
