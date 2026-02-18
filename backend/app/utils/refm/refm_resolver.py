# app/utils/refm/refm_resolver.py

from functools import lru_cache
from typing import Any
from sqlalchemy import inspect
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.cache.refm_cache import RefmCache, RefmData


class RefmResolver:
    """
    Dedicated service for resolving REFM (reference master) values using ForeignKey metadata.
    Fully dynamic — no table/column strings required in calling code.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    # ------------------------------------------------------------------
    # Cached FK → (table, code_column) resolver
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
    # Public API
    # ------------------------------------------------------------------
    async def from_column(
        self,
        *,
        column_attr: InstrumentedAttribute,
        code: str | None,
        value_column: str,
        default: Any = "",
    ) -> Any:
        """
        Resolve a value from REFM table using dynamic FK introspection.

        Example:
            symbol = await resolver.from_column(
                column_attr=LocalizationSettings.currency,
                code="INR",
                value_key="symbol",
                default="?"
            )
        """
        if not code:
            return default

        # Safe extraction of model class (handles Mapped[...] generics in SQLAlchemy 2.0)
        parent = column_attr.parent
        model = parent.class_ if hasattr(parent, "class_") else parent

        column_key = column_attr.key

        try:
            table, code_key = RefmResolver._resolve_refm_target(model, column_key)
        except Exception as exc:
            # Graceful fallback during dev/startup if introspection fails
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"REFM target resolution failed for {model}.{column_key}: {exc}")
            return default

        refm_data: RefmData = await RefmCache.get(session=self.session)
        rows = refm_data.get(table) or []

        lookup = {row.get(code_key): row for row in rows}
        return lookup.get(code, {}).get(value_column, default)