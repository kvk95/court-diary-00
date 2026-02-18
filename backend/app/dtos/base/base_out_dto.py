from typing import TypeVar, Generic, Dict
from pydantic import BaseModel
from app.validators.error_codes import CodeDescription, ErrorCodes

T = TypeVar("T")


class StatusDto(BaseModel):
    code: str
    description: str = ""

    def __init__(self, code: CodeDescription, description: str = "") -> None:
        # bypass BaseModel's default init, enforce CodeDescription
        super().__init__(
            code=code.code,
            description=description or code.description,
        )


class BaseOutDto(BaseModel, Generic[T]):
    status: StatusDto
    result: T

    @classmethod
    def success(cls, result: T, description: str = "Success") -> "BaseOutDto[T]":
        """
        Construct a success response with a single SUCCESS status.
        """
        return cls(
            status=StatusDto(code=ErrorCodes.SUCCESS, description=description),
            result=result,
        )

    @classmethod
    def failure(
        cls,
        code: CodeDescription,
        description: str = "",
    ) -> "BaseOutDto[Dict]":
        """
        Construct a failure response with a single status.
        Always returns BaseOutDto[Dict] with empty result.
        """
        return BaseOutDto[Dict](
            status=StatusDto(code=code, description=description),
            result={},
        )
