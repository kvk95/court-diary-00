# app\utils\utilities.py

import base64
from datetime import datetime, timezone
import hashlib
import hmac
import secrets
import string
from typing import Optional

from app.core.config import settings
from app.validators.password_policy_helper import PasswordPolicy

PASSWORD_LENGTH = 15
PASSWORD_POLICY = PasswordPolicy(
    min_length=8,
    max_length=PASSWORD_LENGTH,
    allowed_specials="@#$%"
)

def generate_password():
    import random

    chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(PASSWORD_POLICY.allowed_specials),
    ]

    all_chars = string.ascii_letters + string.digits + PASSWORD_POLICY.allowed_specials
    chars += [secrets.choice(all_chars) for _ in range(PASSWORD_LENGTH - 4)]

    random.shuffle(chars)
    return ''.join(chars)

# 🔑 Generate & store this key securely (e.g., env var, secret manager)
# DO NOT hardcode it in production
SECRET_KEY = (settings.CIPHER_SECRET_KEY or "b3-2QWAOSouiqeCaZgFzHCaIYGl7RvCRtmK6OExNnqA=").encode()
    
def encode_text(text: str) -> str:
    sig = hmac.new(SECRET_KEY, text.encode(), hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(text.encode() + b"." + sig[:8])
    return token.decode()


def decode_text(encoded_text: str) -> str:
    data = base64.urlsafe_b64decode(encoded_text.encode())
    text, sig = data.rsplit(b".", 1)

    expected_sig = hmac.new(SECRET_KEY, text, hashlib.sha256).digest()[:8]

    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Invalid signature")

    return text.decode()

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert naive datetime to UTC-aware. Leave aware datetimes as-is."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume naive input is in UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_date(value: str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {value}")