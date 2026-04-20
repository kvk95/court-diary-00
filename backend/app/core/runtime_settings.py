# app/core/runtime_settings.py

from app.core.config import settings

_runtime_settings = {}

def get_runtime_setting(key: str, default=None):
    return _runtime_settings.get(key, getattr(settings, key, default))


def set_runtime_settings(data: dict):
    global _runtime_settings
    _runtime_settings = data