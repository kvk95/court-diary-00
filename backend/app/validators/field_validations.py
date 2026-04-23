# app/validators/field_validations.py

import re
from typing import Optional

from app.utils.utilities import PASSWORD_POLICY
from .error_codes import ErrorCodes
from .validation_errors import ValidationErrorDetail



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
        try:
            PASSWORD_POLICY.validate(password)
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
    
    @classmethod
    def validate_enum(cls, enum_class, value, field_name, errors):
        if value is None:
            return None
        try:
            return enum_class(value)
        except ValueError:
            errors.append(
                ValidationErrorDetail(
                    code=ErrorCodes.VALIDATION_ERROR,
                    message=f"Invalid {field_name}"
                )
            )
            return None
