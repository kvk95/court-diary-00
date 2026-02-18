# app/validators/password_policy_helper.py

import re
from .error_codes import ErrorCodes
from .validation_errors import ValidationErrorDetail


class PasswordPolicy:
    """
    Configurable password policy helper.
    Enforces rules like min/max length, required character classes, and allowed specials.
    """

    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 20,
        require_upper: bool = True,
        require_lower: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        allowed_specials: str = "@$#%"
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
        self.require_special = require_special
        self.allowed_specials = allowed_specials

        # Build regex dynamically
        parts = []
        if self.require_lower:
            parts.append("(?=.*[a-z])")
        if self.require_upper:
            parts.append("(?=.*[A-Z])")
        if self.require_digit:
            parts.append("(?=.*\\d)")
        if self.require_special:
            parts.append(f"(?=.*[{re.escape(self.allowed_specials)}])")

        allowed_chars = f"A-Za-z\\d{re.escape(self.allowed_specials)}"
        self.regex = re.compile(
            f"^{''.join(parts)}[{allowed_chars}]{{{self.min_length},{self.max_length}}}$"
        )

    def validate(self, password: str | None) -> None:
        """
        Validate a password against the configured policy.
        Raises ValidationErrorDetail if requirements are not met.
        """
        if not password:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Password is required"
            )
        if not self.regex.match(password):
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message=(
                    f"Password must be {self.min_length}-{self.max_length} chars, "
                    f"include upper, lower, digit, and special ({self.allowed_specials})"
                )
            )
