from __future__ import annotations

import asyncio
import importlib
import pkgutil
import time
from typing import Any, Dict, List, Type, TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import __name__ as package_name
from app.database.models import __path__ as models_path
from app.database.models.base.base_model import (
    BaseModel,
)  # Base class for all ORM models
from app.database.repositories.base.base_repository import BaseRepository, OrmModel

# 🔹 Public cache return type
RefmData: TypeAlias = Dict[str, List[Dict[str, Any]]]


def _discover_refm_models() -> List[Type[OrmModel]]:
    """
    Dynamically discover all reference (Refm*) model classes defined in the
    app.database.models package.

    Scans every module starting with 'refm_' and collects classes that:
    - Start with 'Refm'
    - Are actual classes (not functions, variables, etc.)
    - Are defined in the scanned module
    - Inherit from BaseModel
    - Declare a __tablename__ (ensures it's a concrete table model)

    Returns:
        List of discovered REFM model classes.
    """

    refm_models: List[Type[OrmModel]] = []

    # Iterate over all modules in the package
    for _, modname, ispkg in pkgutil.iter_modules(models_path):
        if not modname.startswith("refm_"):
            continue  # Skip non-refm modules (e.g., __init__.py, other files)

        if ispkg:
            continue  # Skip subpackages if any

        # Import the module
        full_modname = f"{package_name}.{modname}"
        module = importlib.import_module(full_modname)

        # Find classes defined in this module that start with 'Refm'
        for attr_name in dir(module):
            if not attr_name.startswith("Refm"):
                continue

            attr = getattr(module, attr_name)

            if (
                isinstance(attr, type)
                and attr.__module__ == full_modname  # Defined in this module
                and BaseModel in getattr(attr, "__mro__", ())  # Inherits from BaseModel
                and getattr(attr, "__tablename__", None)
                is not None  # Has a table name (extra safety)
            ):
                refm_models.append(attr)

    return refm_models


class RefmCache:
    """
    In-memory singleton cache for all REFM (reference/master) tables.

    Provides fast access to infrequently changing reference data with optional TTL-based
    expiration and manual invalidation support. Thread-safe via asyncio.Lock.
    """

    # 🔹 Config
    TTL_SECONDS: int | None = 300  # Cache validity in seconds (None = no expiration)

    # 🔹 Cache state
    _data: RefmData | None = None
    _last_loaded: float | None = None
    _lock = asyncio.Lock()

    # 🔹 Dynamically discovered models (computed once at import time)
    REFM_MODELS: List[Type[OrmModel]] = _discover_refm_models()

    # ---------------------------
    # Public API
    # ---------------------------

    @classmethod
    async def get(cls, *, session: AsyncSession) -> RefmData:
        """
        Retrieve cached REFM data.

        If cache is empty or expired, loads fresh data from the database.
        Uses async lock to prevent concurrent reloads.

        Args:
            session: Active AsyncSession for database access.

        Returns:
            Dictionary mapping table names to list of row dictionaries.
        """
        async with cls._lock:
            if cls._data is not None and not cls._is_expired():
                print("✅ REFM Cache HIT – returning cached data")
                return cls._data

            print("🔄 REFM Cache MISS/EXPIRED – loading fresh data from database...")
            print(
                f"   Discovered {len(cls.REFM_MODELS)} REFM models: "
                f"{', '.join(model.__tablename__ for model in cls.REFM_MODELS)}"
            )

            cls._data = await cls._load(session=session)
            cls._last_loaded = time.time()

            print(
                f"✅ REFM data successfully loaded and cached "
                f"(TTL: {cls.TTL_SECONDS}s if set)"
            )

            return cls._data

    @classmethod
    def invalidate(cls) -> None:
        """
        Manually invalidate the cache.

        Should be called after any mutation (INSERT/UPDATE/DELETE) on REFM tables
        to ensure subsequent reads get fresh data.
        """
        if cls._data is None:
            print("ℹ️  REFM cache already empty – nothing to invalidate")
            return

        cls._data = None
        cls._last_loaded = None
        print("🗑️  REFM cache manually invalidated")

    # ---------------------------
    # Internals
    # ---------------------------

    @classmethod
    def _is_expired(cls) -> bool:
        """
        Check if cached data has exceeded its TTL.

        Returns:
            True if expired or TTL not configured; False otherwise.
        """
        if cls.TTL_SECONDS is None or cls._last_loaded is None:
            return False
        return (time.time() - cls._last_loaded) > cls.TTL_SECONDS

    @classmethod
    async def _load(cls, *, session: AsyncSession) -> RefmData:
        """
        Load all REFM data from the database using BaseRepository helper.

        Args:
            session: Active AsyncSession.

        Returns:
            Fresh REFM data dictionary.
        """
        data: RefmData = await BaseRepository.get_all_refm_data(
            session=session,
            refm_models=cls.REFM_MODELS,
        )
        return data
