from .error_codes import ErrorCodes
from .validation_errors import (
    ApplicationError,
    ValidationErrorDetail,
    ValidationAggregateError,
)
from .field_validations import FieldValidator


def aggregate_errors(errors: list[ValidationErrorDetail]) -> None:
    """
    Raise a ValidationAggregateError if the list of errors is non-empty.
    Keeps service code clean: just call aggregate_errors(errors).
    """
    if errors:
        raise ValidationAggregateError(errors=errors)


__all__ = [
    "ErrorCodes",
    "ApplicationError",
    "ValidationErrorDetail",
    "ValidationAggregateError",
    "FieldValidator",
    "aggregate_errors",
]
