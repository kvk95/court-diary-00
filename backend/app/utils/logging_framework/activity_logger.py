from datetime import datetime

from ...core.context import get_request_context
from .log_types import LogType
from .logging_util import add_to_queue


async def log_activity(
    action: str,
    actor_user_id: str | None = None,
    actor_company_id: int | None = None,
    target: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
):
    """
    Enqueue an activity log event.
    Routing (none / console / db / file) is handled by the queue worker.
    """

    ctx = get_request_context()
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "actor_user_id": actor_user_id or (ctx.get("user_id") if ctx else None),
        "actor_company_id": actor_company_id or (ctx.get("company_id") if ctx else None),
        "target": target,
        "metadata": metadata or {},
        "ip_address": ip_address or (ctx.get("ip") if ctx else None),
    }
    
    await add_to_queue(log_type= LogType.ACTIVITY, payload =  payload)
