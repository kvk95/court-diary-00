# app/whatsapp/flow_registry.py

from typing import Callable, Awaitable

FlowHandler = Callable[..., Awaitable[str]]

FLOW_REGISTRY: dict[str, FlowHandler] = {}
START_REGISTRY: dict[str, FlowHandler] = {}

# app/whatsapp/flow_registry.py

def register_flow(name: str, *, start: FlowHandler, handler: FlowHandler):
    FLOW_REGISTRY[name] = handler
    START_REGISTRY[name] = start