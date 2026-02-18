from app.validators.error_codes import CodeDescription, ErrorCodes

class ApplicationError(Exception):
    def __init__(
        self,
        code: CodeDescription = ErrorCodes.VALIDATION_ERROR,
        message: str = ErrorCodes.VALIDATION_ERROR.description,
    ):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationErrorDetail(ApplicationError):
    def __init__(self, code: CodeDescription, message: str):
        super().__init__(code=code,message=message)


class ValidationAggregateError(ApplicationError):
    def __init__(self, errors: list[ValidationErrorDetail], code: CodeDescription = ErrorCodes.VALIDATION_ERROR):
        super().__init__(code=code)
        self.errors = errors
