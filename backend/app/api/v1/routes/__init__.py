# app/api/v1/routes/__init__.py

import importlib
import pkgutil
from fastapi import APIRouter
from app.api.v1.routes import __path__ as routes_path, __name__ as routes_pkg
from .base.base_controller import BaseController

v1_router = APIRouter()

def _discover_controllers():
    controllers = []

    # Scan modules inside app.api.v1.routes
    for _, modname, ispkg in pkgutil.iter_modules(routes_path):
        if not modname.endswith("_controller") or ispkg:
            continue

        full_modname = f"{routes_pkg}.{modname}"

        module = importlib.import_module(full_modname)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseController)
                and attr is not BaseController
                and attr.__module__ == full_modname
            ):
                instance = attr()
                controllers.append(instance)

    return controllers

# Auto-register all discovered controllers
for controller in _discover_controllers():
    v1_router.include_router(controller.router)
