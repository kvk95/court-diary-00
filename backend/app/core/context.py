# app\core\context.py

from contextvars import ContextVar
from typing import Any, Dict, Optional

_request_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "_request_context", default=None
)


def set_request_context(**kwargs):
    """
    Safely set or update request-scoped context values.
    """
    ctx = _request_context.get() or {}
    new_ctx = {**ctx, **{k: v for k, v in kwargs.items() if v is not None}}
    _request_context.set(new_ctx)


def get_request_context() -> Dict[str, Any]:
    """
    Get current request context (always returns a dict).
    """
    return _request_context.get() or {}


def clear_request_context():
    """
    Clear request context (typically called at end of request).
    """
    _request_context.set(None)
