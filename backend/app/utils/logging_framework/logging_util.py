# app\utils\logging_framework\logging_util.py

import re

from .log_types import LogType
from .queue_manager import get_queue_manager
from app.core.context import get_request_context


async def add_to_queue(log_type: LogType, payload: dict):
    ctx = get_request_context()

    payload["_ctx"] = {
        "request_id": ctx.get("request_id"),
        "user_id": ctx.get("user_id"),
        "company_id": ctx.get("company_id"),
        "ip": ctx.get("ip"),
    }
    payload["request_id"] = ctx.get("request_id")
    
    qm = get_queue_manager()
    await qm.enqueue(log_type= log_type, payload =  payload)
    

def mask_sensitive(params, sensitive_keys=None):
    """
    Recursively mask sensitive data in dicts, lists, tuples, or primitives.
    Supports positional parameters (e.g., SQL args) by scanning values for emails, etc.
    """
    if sensitive_keys is None:
        sensitive_keys = [
            "password", "token", "refresh_token", "access_token", "auth_token",
            "session_id", "jwt", "cookie", "credit_card", "card_number", "cc_number",
            "cvv", "cvc", "card_code", "api_key", "secret", "client_secret",
            "email", "phone", "phone_number", "mobile", "ssn", "tax_id"
        ]

    sensitive_set = {k.lower() for k in sensitive_keys}

    # Patterns to detect sensitive values even without keys
    EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    PHONE_PATTERN = re.compile(r'\+?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}$')
    CARD_PATTERN = re.compile(r'\d{12,19}')

    def is_likely_email(value):
        return isinstance(value, str) and EMAIL_PATTERN.match(value.strip())

    def is_likely_phone(value):
        return isinstance(value, str) and PHONE_PATTERN.search(value)

    def is_likely_card(value):
        return isinstance(value, str) and CARD_PATTERN.search(value.replace(' ', ''))

    def mask_email(value):
        if not isinstance(value, str) or '@' not in value:
            return "****"
        local, domain = value.split('@', 1)
        masked_local = local[0] + "***" if len(local) > 1 else "***"
        return f"{masked_local}@{domain}"

    def mask_phone(value):
        digits = re.sub(r'\D', '', str(value))
        return "******" + digits[-4:] if len(digits) >= 4 else "****"

    def mask_card(value):
        digits = re.sub(r'\D', '', str(value))
        return "**** **** **** " + digits[-4:] if len(digits) >= 4 else "****"

    def mask_value_by_content(value):
        """Mask based on value pattern when no key is available"""
        if is_likely_email(value):
            return mask_email(value)
        if is_likely_phone(value):
            return mask_phone(value)
        if is_likely_card(value):
            return mask_card(value)
        return value  # not sensitive by pattern

    def should_mask_key(key):
        return isinstance(key, str) and any(s in key.lower() for s in sensitive_set)

    def apply_mask_for_key(key, value):
        lower_key = key.lower()
        if any(k in lower_key for k in ["password", "token", "secret", "cvv", "ssn", "jwt", "cookie"]):
            return "****"
        if "email" in lower_key:
            return mask_email(value)
        if "phone" in lower_key:
            return mask_phone(value)
        if "card" in lower_key:
            return mask_card(value)
        return "****"

    def mask_recursive(obj):
        if isinstance(obj, dict):
            masked = {}
            for k, v in obj.items():
                if should_mask_key(k):
                    masked[k] = apply_mask_for_key(k, v)
                else:
                    masked[k] = mask_recursive(v)
            return masked

        elif isinstance(obj, (list, tuple)):
            masked_list = []
            for item in obj:
                # If it's a simple value and looks sensitive → mask by content
                if isinstance(item, (str, int, float)) and not isinstance(item, bool):
                    if any(s in str(item).lower() for s in ["pass", "token", "secret", "cvv", "ssn"]):
                        masked_list.append("****")
                    elif is_likely_email(item):
                        masked_list.append(mask_email(item))
                    elif is_likely_phone(item):
                        masked_list.append(mask_phone(item))
                    elif is_likely_card(item):
                        masked_list.append(mask_card(item))
                    else:
                        masked_list.append(mask_recursive(item))  # recurse if nested
                else:
                    masked_list.append(mask_recursive(item))
            return type(obj)(masked_list)  # Preserve tuple vs list

        else:
            # Primitive: check if it looks like sensitive data
            return mask_value_by_content(obj)

    if params is None:
        return None

    return mask_recursive(params)