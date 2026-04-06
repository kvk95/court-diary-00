# app\utils\utilities.py

import secrets
import string

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