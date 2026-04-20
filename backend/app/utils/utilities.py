# app\utils\utilities.py

import base64
import hashlib
import hmac
import secrets
import string

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