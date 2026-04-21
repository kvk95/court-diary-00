# app/api/v1/routes/base/base_controller.py

import inspect
from abc import ABC
from functools import wraps
from typing import Any, Optional, Sequence, TypeVar, List, Tuple, Callable  
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

        if not self.tags:
            self.tags = [self.__class__.__name__]

        self.router = APIRouter(prefix=f"/{self.CONTROLLER_NAME}", tags=list(self.tags))
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
        methods_with_order = self._get_methods_in_definition_order()
        
        # Sort: static/literal paths before parameterized ones
        def path_priority(item):
            _, method = item
            rule, _ = method._route_info
            # Count path params — more params = lower priority
            return rule.count("{")
        
        methods_with_order.sort(key=path_priority)
        
        for name, method in methods_with_order:
            route_info = getattr(method, "_route_info", None)
            if not route_info:
                continue

            rule, options = route_info
            options = dict(options)  # ← defensive copy so pop doesn't mutate stored dict
            methods = options.pop("methods", ["GET"])

            for http_method in [m.upper() for m in methods]:
                decorator = getattr(self.router, http_method.lower(), None)
                if decorator is None:
                    raise ValueError(f"Invalid HTTP method: {http_method} in {name}")
                decorator(rule, **options)(method)

    def _get_methods_in_definition_order(self) -> List[Tuple[str, Callable[..., Any]]]:
        """
        Get methods in class definition order, not alphabetical.
        Uses __dict__ which preserves insertion order (Python 3.7+).
        """
        methods = []
        
        # Walk through class hierarchy
        for cls in type(self).__mro__:
            if cls is BaseController:
                continue
                
            # __dict__ preserves definition order (Python 3.7+)
            for name, attr in cls.__dict__.items():
                if inspect.isfunction(attr) or inspect.ismethod(attr):
                    # Check if it's actually a route (has _route_info)
                    if hasattr(attr, '_route_info'):
                        methods.append((name, getattr(self, name)))
        
        return methods

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