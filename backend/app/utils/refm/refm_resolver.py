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
    This allows you to dynamically look up descriptive values (like names, symbols, etc.)
    from reference tables without hardcoding table or column names.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._lookup_cache = {}

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

    async def get_value(
            self,
            desc_map: dict,
            code:str | None,
            default: Any = "",

    )-> str:
        return desc_map.get(code,default)

    async def get_desc_map(
        self,
        *,
        column_attr: InstrumentedAttribute,
        value_column: InstrumentedAttribute,
    ) -> dict:
        # Resolve table + code column
        parent = column_attr.parent
        model = parent.class_ if hasattr(parent, "class_") else parent
        column_key = column_attr.key

        table, code_key = RefmResolver._resolve_refm_target(model, column_key)
        table = table.upper()

        # Get cached data
        refm_data: RefmData = await RefmCache.get(session=self.session)
        rows = refm_data.get(table) or []

        # Cache key includes value_column also
        cache_key = (table, code_key, value_column.key)

        if cache_key not in self._lookup_cache:
            self._lookup_cache[cache_key] = {
                row.get(code_key): row.get(value_column.key)
                for row in rows
            }

        return self._lookup_cache[cache_key]

    async def from_column(
        self,
        *,
        column_attr: InstrumentedAttribute,
        code: str | None,
        value_column: InstrumentedAttribute,
        default: Any = "",
    ) -> Any:
        """
        Resolve a descriptive value from a REFM (reference master) table.

        Parameters
        ----------
        column_attr : InstrumentedAttribute
            The SQLAlchemy model attribute that holds the foreign key reference.
            Example: `RefmCaseStatus.code` (points to a currency code FK).

        code : str | None
            The code value you want to look up in the REFM table.
            Example: `c.status_code`. If `None`, the `default` is returned.

        value_column : InstrumentedAttribute
            The target column in the REFM table whose value you want to retrieve.
            Example: `RefmCaseStatus.description`.

        default : Any, optional
            Fallback value if the lookup fails or the code is missing.
            Defaults to empty string `""`.

        Returns
        -------
        Any
            The resolved value from the REFM table, or the `default` if not found.

        Examples
        --------
        # Example 1: Currency symbol lookup
        symbol = await resolver.from_column(
            column_attr=LocalizationSettings.currency,
            code="INR",
            value_column=RefmCurrency.symbol,
            default="?"
        )
        # Returns: "₹"

        # Example 2: Case status description lookup
        status_description = await resolver.from_column(
            column_attr=RefmCaseStatus.code,
            code=c.status_code,
            value_column=RefmCaseStatus.description,
            default="Unknown"
        )
        # Returns: "Closed" or "Pending", depending on c.status_code
        """
        if not code:
            return default

        try:
            desc_map = await self.get_desc_map(
                column_attr=column_attr,
                value_column=value_column,
            )
        except Exception:
            return default

        return desc_map.get(code, default)