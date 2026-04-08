# app/utils/refm/refm_resolver.py

from functools import lru_cache
from typing import Any
from sqlalchemy import inspect
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData


class RefmResolver:
    """
    Dedicated Service for resolving REFM (reference master) values using ForeignKey metadata.
    Supports both simple description lookups and full row mapping.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._lookup_cache: dict = {}

    @property
    def session(self) -> AsyncSession:
        return self._session

    # ------------------------------------------------------------------
    # Internal: Resolve FK → (table, code_column)
    # ------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=256)
    def _resolve_refm_target(model: type, column_key: str) -> tuple[str, str]:
        mapper = inspect(model)
        column = mapper.columns.get(column_key)

        if column is None:
            raise ValueError(f"Column '{column_key}' not found on model {model.__name__}")

        if not column.foreign_keys:
            raise ValueError(f"Column '{model.__name__}.{column_key}' has no ForeignKey")

        fk = next(iter(column.foreign_keys))
        return fk.column.table.name, fk.column.key

    # ------------------------------------------------------------------
    # Core Method: Get Full Reference Map (NEW + RECOMMENDED)
    # ------------------------------------------------------------------
    async def get_refm_map(
        self,
        *,
        column_attr: InstrumentedAttribute,
    ) -> dict:
        """
        Returns a mapping:  code → full_row_dict (containing ALL columns from the REFM table)
        
        This is the most flexible method. Use this when you need more than one column.
        """
        # Resolve table and code column using FK metadata
        parent = column_attr.parent
        model = parent.class_ if hasattr(parent, "class_") else parent
        column_key = column_attr.key

        table, code_key = RefmResolver._resolve_refm_target(model, column_key)
        table = table.upper()

        # Get reference data from cache
        refm_data: RefmData = await RefmCache.get(session=self.session)
        rows = refm_data.get(table) or []

        # Cache key (we return full rows, so value_column is not needed)
        cache_key = (table, code_key, "__full_row__")

        if cache_key not in self._lookup_cache:
            lookup: dict = {}
            for row in rows:
                code = row.get(code_key)
                if code is not None:        # Skip rows with null code
                    # Convert to plain dict with all columns (safe for different row types)
                    full_row = dict(row) if hasattr(row, 'keys') else {**row}
                    lookup[code] = full_row

            self._lookup_cache[cache_key] = lookup

        return self._lookup_cache[cache_key]

    # ------------------------------------------------------------------
    # Legacy Method: Simple code → single value (kept for backward compatibility)
    # ------------------------------------------------------------------
    async def get_desc_map(
        self,
        *,
        column_attr: InstrumentedAttribute,
        value_column: InstrumentedAttribute,
    ) -> dict:
        """
        Returns a simple mapping: code → value (from a single column)
        Uses get_refm_map internally to avoid duplication.
        """
        full_map = await self.get_refm_map(column_attr=column_attr)

        value_key = value_column.key

        return {
            code: row.get(value_key)
            for code, row in full_map.items()
        }

    # ------------------------------------------------------------------
    # Convenience Method
    # ------------------------------------------------------------------
    async def get_value(
        self,
        desc_map: dict,
        code: str | None,
        default: Any = "",
    ) -> str:
        """Simple helper to safely get value from a desc_map."""
        if code is None:
            return default
        return desc_map.get(code, default)

    async def from_column(
        self,
        *,
        column_attr: InstrumentedAttribute,
        code: str | None,
        value_column: InstrumentedAttribute,
        default: Any = "",
    ) -> Any:
        """
        Resolve a descriptive value from a REFM table using ForeignKey metadata.
        """
        if not code:
            return default

        try:
            desc_map = await self.get_desc_map(
                column_attr=column_attr,
                value_column=value_column,
            )
            return desc_map.get(code, default)
        except Exception:
            return default