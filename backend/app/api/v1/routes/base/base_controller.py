import inspect
from abc import ABC
from functools import wraps
from typing import Optional, Sequence, TypeVar

from fastapi import APIRouter

from app.dtos.base.base_out_dto import BaseOutDto

T = TypeVar("T")


class BaseController(ABC):
    CONTROLLER_NAME: Optional[str] = None
    tags: Sequence[str] = ()
    router: Optional[APIRouter] = None

    def __init__(self) -> None:

        if not self.CONTROLLER_NAME:
            self.CONTROLLER_NAME = (
                (type(self).__name__).removesuffix("Controller").lower()
            )

        # Auto-add class name to tags if empty
        if not self.tags:
            self.tags = [self.__class__.__name__]

        self.router = APIRouter(prefix=f"/{self.CONTROLLER_NAME}", tags=list(self.tags))
        # Register routes after initialization
        self._register_routes()

    @staticmethod
    def route(rule: str, **options):
        """Decorator to mark methods as routes"""

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            wrapper._route_info = (rule, options)  # type: ignore[attr-defined]
            return wrapper

        return decorator

    def _register_routes(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            route_info = getattr(method, "_route_info", None)
            if not route_info:
                continue

            rule, options = route_info
            methods = options.pop("methods", ["GET"])

            for http_method in [m.upper() for m in methods]:
                decorator = getattr(self.router, http_method.lower(), None)
                if decorator is None:
                    raise ValueError(f"Invalid HTTP method: {http_method} in {name}")

                # This applies: router.get("/path", summary=...)(method)
                decorator(rule, **options)(method)

    @staticmethod
    def get(rule: str, **options):
        options.setdefault("methods", ["GET"])
        return BaseController.route(rule, **options)

    @staticmethod
    def post(rule: str, **options):
        options.setdefault("methods", ["POST"])
        return BaseController.route(rule, **options)

    @staticmethod
    def put(rule: str, **options):
        options.setdefault("methods", ["PUT"])
        return BaseController.route(rule, **options)

    @staticmethod
    def delete(rule: str, **options):
        options.setdefault("methods", ["DELETE"])
        return BaseController.route(rule, **options)

    @staticmethod
    def success(result: T, description: str = "Success") -> BaseOutDto[T]:
        return BaseOutDto.success(result=result, description=description)
