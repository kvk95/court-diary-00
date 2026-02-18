# app/validators/field_validations.py

import re
from typing import Optional
from .error_codes import ErrorCodes
from .validation_errors import ValidationErrorDetail
from .password_policy_helper import PasswordPolicy

from app.validators.password_policy_helper import PasswordPolicy


class FieldValidator:
    """
    Provides reusable format validations for fields like email, password, phone, etc.
    Each validator returns None if valid, or a ValidationErrorDetail if invalid.
    """

    EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")  # optional international format

    @classmethod
    def validate_email(cls, email: Optional[str]) -> Optional[ValidationErrorDetail]:
        if not email:
            return ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Email is required"
            )
        if not cls.EMAIL_REGEX.match(email):
            return ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Invalid email format"
            )
        return None

    @classmethod
    def validate_password(cls, password: Optional[str]) -> Optional[ValidationErrorDetail]:
        """
        Validate password using PasswordPolicy helper.
        Returns None if valid, or ValidationErrorDetail if invalid.
        """
        policy = PasswordPolicy(min_length=8, max_length=20, allowed_specials="@#$%")
        try:
            policy.validate(password)
        except ValidationErrorDetail as e:
            return e
        return None

    @classmethod
    def validate_phone(cls, phone: Optional[str]) -> Optional[ValidationErrorDetail]:
        if phone and not cls.PHONE_REGEX.match(phone):
            return ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="Invalid phone number format"
            )
        return None
