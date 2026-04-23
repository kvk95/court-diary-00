from typing import Final

class CodeDescription:
    def __init__(self, Code: str, Description: str) -> None:
        self.code = Code
        self.description = Description


class ErrorCodes():
    SUCCESS: Final[CodeDescription] = CodeDescription(Code = "S", Description="Success")
    FAILURE: Final[CodeDescription] = CodeDescription(Code = "F", Description="Failure")
    NOT_FOUND: Final[CodeDescription] = CodeDescription(Code = "E001", Description="No matching Record")
    VALIDATION_ERROR: Final[CodeDescription] = CodeDescription(Code = "E001", Description="Validation Failed")
    PERMISSION_DENIED: Final[CodeDescription] = CodeDescription(Code = "401", Description="Unauthorized")
    INTEGRITY_ERROR: Final[CodeDescription] = CodeDescription(Code = "E007", Description="Record being modified by another user")

class ErrorConstants:
    INVALID_INPUT = "Invalid input"
    DUPLICATE_ENTRY = "Duplicate entry"
    NOT_FOUND = "Not found"
