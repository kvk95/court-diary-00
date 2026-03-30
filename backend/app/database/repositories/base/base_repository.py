# app\database\repositories\base\base_repository.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    Protocol,
    ClassVar,
    runtime_checkable,
)

from fastapi import HTTPException
from sqlalchemy import MetaData, Table, func, insert, select, update
from sqlalchemy import Boolean
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression, ColumnElement
from sqlalchemy.sql.schema import Column

from app.core.context import get_request_context
from app.database.models.base.base_model import BaseModel
from .model_helpers import get_writable_columns

ModelType = TypeVar("ModelType", bound=BaseModel)
FilterKey = Union[InstrumentedAttribute[Any], ColumnElement[Any], Any]
filters: Optional[Dict[FilterKey, Any]] = None


@runtime_checkable
class OrmModel(Protocol):
    """
    Structural typing for SQLAlchemy ORM models.
    Any ORM model with __tablename__ is accepted.
    """

    __tablename__: ClassVar[str]


class BaseRepository(Generic[ModelType]):
    """
    Production-hardened base repository for SQLAlchemy 2.0 async.

    Design principles:
    - Filters use column objects (ColumnElement) with equality-only semantics
    - Where accepts advanced SQLAlchemy expressions (>, <, IN, AND/OR, etc.)
    - Joins accept only column/relationship InstrumentedAttribute
    - Order_by accepts ColumnElement or SQLAlchemy order expressions (e.g., column.desc())
    - Soft-delete awareness across all reads
    - Audit fields support (created_by, updated_by, deleted_by)
    - Composite and single primary key support via id_values fallback in get_by_id

    Parameters used across methods:
    - filters: Dict[ColumnElement, Any]
      Equality-only comparisons; keys must be SQLAlchemy column objects.
    - where: Sequence[Any]
      Advanced SQLAlchemy expressions; validated at runtime for correctness.
    - joins: Sequence[InstrumentedAttribute]
      Relationship/column attributes used for join().
    - order_by: Sequence[ColumnElement]
      Column attributes or order expressions for ordering.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.WRITABLE_FIELDS = get_writable_columns(model)

    # ────────────────────────────────────────────────
    # ──────── FIELD / LOGGING HELPERS ────────
    # ────────────────────────────────────────────────

    def map_fields_to_db_column(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter incoming data to only writable fields for this model.
        Skips None values to avoid unwanted overwrites of nullable columns.
        """
        return {
            k: v for k, v in data.items() if k in self.WRITABLE_FIELDS and v is not None
        }

    def _log_stmt(self, stmt, session: AsyncSession):
        """
        Log a SQL statement with literal binds where possible.
        Non-critical; intended for debugging visibility.
        """
        try:
            compiled = stmt.compile(
                dialect=session.bind.dialect if session.bind else None,
                compile_kwargs={"literal_binds": True},
            )
            sql_str = str(compiled)
        except Exception:
            # Fallback for JSON, ARRAY, and other exotic types
            sql_str = str(stmt)

        # print("┌─ EXECUTED SQL " + "─" * 60 + "┐")
        # print(sql_str)
        # print("└" + "─" * 75 + "┘\n")

    async def execute(self, stmt, session: AsyncSession):
        """
        Centralized execute with logging.
        """
        stmt = self._apply_chamber_id_filter(stmt)
        self._log_stmt(stmt, session)
        return await session.execute(stmt)

    async def fetch_scalars(self, session: AsyncSession, stmt):
        result = await self.execute(stmt=stmt, session=session)
        return result.scalars().all()


    async def fetch_first(self, session: AsyncSession, stmt):
        result = await self.execute(stmt=stmt, session=session)
        return result.scalars().first()


    async def fetch_scalar(self, session: AsyncSession, stmt):
        result = await self.execute(stmt=stmt, session=session)
        return result.scalar()


    async def fetch_scalar_one(self, session: AsyncSession, stmt):
        result = await self.execute(stmt=stmt, session=session)
        return result.scalar_one()

    # ────────────────────────────────────────────────
    # ──────── VALIDATION HELPERS ────────
    # ────────────────────────────────────────────────

    def _validate_query_params(
        self,
        *,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
    ) -> None:
        """
        Validate query parameters to ensure strict use of SQLAlchemy column objects
        and expressions. Raises TypeError with clear messages if invalid types are found.

        - filters: Dict[column_attr, value] — keys must be ColumnElement
        - where: Sequence[SQLAlchemy expressions] — allowed BinaryExpression or ColumnElement
        - joins: Sequence[InstrumentedAttribute] — must be ColumnElement
        - order_by: Sequence[column_attr or order expr] — ColumnElement or UnaryExpression
        """
        if filters:
            for column in filters.keys():
                if not isinstance(
                    column, (InstrumentedAttribute, Column, ColumnElement)
                ):
                    raise TypeError(
                        "filters must use SQLAlchemy model columns (InstrumentedAttribute / Column / ColumnElement) as keys"
                    )

        if where:
            for condition in where:
                # Accept comparisons and boolean composed expressions (BinaryExpression),
                # and also raw column attributes in case user passes a simple column.bool()
                if not isinstance(condition, (ColumnElement, BinaryExpression)):
                    raise TypeError(
                        "where must contain SQLAlchemy column objects or binary expressions"
                    )

        if joins:
            for join_target in joins:
                if not isinstance(join_target, ColumnElement):
                    raise TypeError(
                        "joins must use model column/relationship attributes (ColumnElement)"
                    )

        if order_by:
            for order in order_by:
                if not isinstance(order, ColumnElement):
                    raise TypeError(
                        "order_by must be SQLAlchemy column expressions: column.asc(), column.desc(), func.*, etc."
                    )

    # ────────────────────────────────────────────────
    # ──────── PRIVATE HELPERS ────────
    # ────────────────────────────────────────────────    

    def _apply_chamber_id_filter(self, stmt: Select) -> Select:
        """
        Apply chamber_id_ filter if the model has chamber_id.
        Supports two conventions:
        - deleted_ind: bool flag
        - deleted_date: nullable datetime when deleted
        """
        ctx = get_request_context()
        chamber_id = cast(str, ctx.get("chamber_id"))
        if hasattr(self.model, "chamber_id"):
            stmt = stmt.where(self.model.chamber_id == chamber_id)
        return stmt

    def _apply_soft_delete_filter(self, stmt: Select) -> Select:
        """
        Apply soft-delete filter if the model supports it.
        Supports two conventions:
        - deleted_ind: bool flag
        - deleted_date: nullable datetime when deleted
        """
        if hasattr(self.model, "deleted_ind"):
            stmt = stmt.where(self.model.deleted_ind.is_(False))
        if hasattr(self.model, "deleted_date"):
            stmt = stmt.where(self.model.deleted_date.is_(None))
        return stmt

    def _paginate(
        self,
        stmt: Select,
        limit: Optional[int] = 50,
        offset: int = 0,
    ) -> Select:
        """
        Apply limit/offset pagination.
        """
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return stmt

    def _pk_names(self) -> List[str]:
        """
        Return a list of primary key column names.
        Supports single and composite primary keys.
        """
        return [col.name for col in self.model.__mapper__.primary_key]

    def _pk_filters_from_values(
        self,
        id_values: Optional[Union[Any, Dict[str, Any]]],
    ) -> List[BinaryExpression]:
        """
        Build equality filters for primary key(s) using id_values.

        - Single PK: id_values is scalar
        - Composite PK: id_values is dict with all PK field names
        """
        if id_values is None:
            raise ValueError(
                "id_values must be provided when filters/where are not supplied"
            )

        pk_fields = self._pk_names()

        if len(pk_fields) == 1:
            # Single PK → scalar value expected
            field = pk_fields[0]
            column = getattr(self.model, field)
            return [column == id_values]

        # Composite PK → dict expected with all pk fields
        if not isinstance(id_values, dict):
            raise ValueError(
                f"Composite primary key for {self.model.__name__} requires id_values as dict "
                f"with keys {pk_fields}, got {id_values}"
            )
        missing = set(pk_fields) - set(id_values.keys())
        if missing:
            raise ValueError(f"Missing keys in id_values for composite PK: {missing}")

        return [getattr(self.model, f) == id_values[f] for f in pk_fields]

    def _apply_common_query_parts(
        self,
        *,
        base_select: Select,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
    ) -> Select:
        """
        Apply filters, where, joins, order_by, and soft-delete to a base SELECT.
        Assumes parameters already validated via _validate_query_params.
        """
        stmt = base_select

        # Joins first to ensure columns/conditions from joined tables work
        if joins:
            for join_target in joins:
                stmt = stmt.join(join_target)

        # Equality filters: {column: value}
        if filters:
            for column, value in filters.items():
                stmt = stmt.where(column == value)

        # Advanced expressions
        if where:
            stmt = stmt.where(*where)

        # Soft delete
        stmt = self._apply_soft_delete_filter(stmt)

        # Ordering
        if order_by:
            stmt = stmt.order_by(*order_by)

        return stmt

    def _set_audit_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ctx = get_request_context()
        user_id = ctx.get("user_id")
        chamber_id = cast(str, ctx.get("chamber_id"))

        result = data.copy()

        # ─────────────────────────────────────────────
        # 🔥 PRIMARY KEY HANDLING
        # ─────────────────────────────────────────────
        pk_columns = self.model.__table__.primary_key.columns
        print("*********************** \n\n\n")
        for col in pk_columns:
            col_name = col.name
            col_type = col.type
            val = result.get(col_name)

            col_length = getattr(col_type, "length", None)

            # Detect UUID-like PK
            is_uuid_pk = (
                col_length == 36 and col_name.lower().endswith("id")
            )

            print(f"*******************{col_name}::{val}")

            if is_uuid_pk:
                if val is None or val == "":
                    result[col_name] = self.model.generate_uuid()
                    print(f"*******************{col_name}::{result[col_name]}")
            else:
                # Non-UUID PK → let DB handle
                if col_name in result and result[col_name] is None:
                    del result[col_name]
        print("*********************** \n\n\n")

        # ─────────────────────────────────────────────
        # 🔹 AUDIT FIELDS
        # ─────────────────────────────────────────────
        if user_id:
            if hasattr(self.model, "created_by") and "created_by" not in result:
                result["created_by"] = user_id

            if hasattr(self.model, "updated_by") and "updated_by" not in result:
                result["updated_by"] = user_id

            if hasattr(self.model, "user_id") and "user_id" not in result:
                result["user_id"] = user_id

        if hasattr(self.model, "chamber_id") and "chamber_id" not in result:
            result["chamber_id"] = chamber_id

        return result

    async def _do_update(
        self,
        session: AsyncSession,
        filters_exprs: Sequence[BinaryExpression],
        data: Dict[str, Any],
    ) -> Optional[ModelType]:
        """
        Perform DB-side UPDATE and reload the entity using the same filters.
        Reused by update() and upsert() to avoid duplication.
        """
        update_data = data.copy()
        ctx = get_request_context()
        user_id = ctx.get("user_id")
        chamber_id = cast(str, ctx.get("chamber_id"))
        if hasattr(self.model, "updated_by"):
            update_data["updated_by"] = user_id
        if hasattr(self.model, "chamber_id"):
                update_data["chamber_id"] = chamber_id

        stmt = (
            update(self.model)
            .where(*filters_exprs)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.execute(stmt, session)

        reload_stmt = select(self.model).where(*filters_exprs)
        reload_stmt = self._apply_soft_delete_filter(reload_stmt)
        
        result = await self.execute(reload_stmt, session)
        return result.scalars().first()

    # ────────────────────────────────────────────────
    # ──────── READ OPERATIONS ────────
    # ────────────────────────────────────────────────

    async def get_by_id(
        self,
        session: AsyncSession,
        *,
        id_values: Optional[Union[Any, Dict[str, Any]]] = None,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
    ) -> Optional[ModelType]:
        """
        Retrieve a single record. Two modes:
        - If filters/where provided → use them
        - Else → fallback to primary key equality using id_values (scalar for single PK, dict for composite PK)
        """
        self._validate_query_params(
            filters=filters, where=where, joins=joins, order_by=order_by
        )

        if filters or where:
            base = select(self.model)
            stmt = self._apply_common_query_parts(
                base_select=base,
                filters=filters,
                where=where,
                joins=joins,
                order_by=order_by,
            )
        else:
            # Fallback to PK lookup
            pk_filters = self._pk_filters_from_values(id_values)
            base = select(self.model).where(*pk_filters)
            stmt = self._apply_soft_delete_filter(base)

        result = await self.execute(stmt=stmt, session=session)
        return result.scalars().first()

    async def get_first(
        self,
        session: AsyncSession,
        *,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
    ) -> Optional[ModelType]:
        """
        Return the first matching record using filters/where with optional joins and ordering.
        """
        self._validate_query_params(
            filters=filters, where=where, joins=joins, order_by=order_by
        )

        base = select(self.model)
        stmt = self._apply_common_query_parts(
            base_select=base,
            filters=filters,
            where=where,
            joins=joins,
            order_by=order_by,
        )

        result = await self.execute(stmt=stmt, session=session)
        return result.scalars().first()

    async def list_all(
        self,
        session: AsyncSession,
        *,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
    ) -> List[ModelType]:
        """
        Return all matching records. No implicit pagination; use list_paginated for controlled retrieval.
        """
        self._validate_query_params(
            filters=filters, where=where, joins=joins, order_by=order_by
        )

        base = select(self.model)
        stmt = self._apply_common_query_parts(
            base_select=base,
            filters=filters,
            where=where,
            joins=joins,
            order_by=order_by,
        )

        result = await self.execute(stmt=stmt, session=session)
        return cast(List[ModelType], result.scalars().all())

    async def list_paginated(
        self,
        session: AsyncSession,
        *,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        joins: Optional[Sequence[InstrumentedAttribute]] = None,
        order_by: Optional[Sequence[ColumnElement[Any]]] = None,
        page: int = 1,
        limit: int = 50,
        distinct: bool = False,
    ) -> Tuple[List[ModelType], int]:
        """
        Fetch a paginated list with optional filtering, where, joins, distinct, and ordering.
        Returns (items, total_count) where total_count is computed before pagination.
        """
        self._validate_query_params(
            filters=filters, where=where, joins=joins, order_by=order_by
        )

        if page < 1:
            page = 1
        if limit < 1:
            limit = 1

        base = select(self.model)
        stmt = self._apply_common_query_parts(
            base_select=base,
            filters=filters,
            where=where,
            joins=joins,
            order_by=None,  # defer ordering until after count subquery
        )

        if distinct:
            stmt = stmt.distinct()

        # Count total BEFORE pagination (strip ordering in subquery)
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = await session.scalar(count_stmt) or 0

        # Apply ordering now
        if not order_by:
            # Default ordering: first PK column asc
            pk_names = self._pk_names()
            if pk_names:
                pk_col = getattr(self.model, pk_names[0], None)
                if isinstance(pk_col, ColumnElement):
                    order_by = [pk_col.asc()]
        if order_by:
            stmt = stmt.order_by(*order_by)

        # Pagination
        stmt = stmt.offset((page - 1) * limit).limit(limit)

        result = await self.execute(stmt=stmt, session=session)
        items = result.scalars().all()
        return list(items), int(total)

    # ────────────────────────────────────────────────
    # ──────── WRITE OPERATIONS ────────
    # ────────────────────────────────────────────────

    async def create(
        self,
        session: AsyncSession,
        *,
        data: Dict[str, Any],
        deleted_ind: Optional[bool] = False,
    ) -> ModelType:
        """
        Create a new record.
        - data should already be filtered via map_fields_to_db_column
        - created_by is injected to audit fields if supported
        - deleted_ind defaults to False unless explicitly set on the model
        """
        create_data = self._set_audit_fields(data)

        if hasattr(self.model, "deleted_ind") and "deleted_ind" not in create_data:
            create_data["deleted_ind"] = deleted_ind

        # Log INSERT for visibility; ORM performs actual insert
        self._log_stmt(insert(self.model).values(**create_data), session)

        obj = self.model(**create_data)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def update(
        self,
        session: AsyncSession,
        *,
        id_values: Optional[Union[Any, Dict[str, Any]]] = None,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        data: Dict[str, Any],
    ) -> ModelType:
        """
        Update an existing record.

        Target selection:
        - If filters/where provided → use them
        - Else → fallback to primary key equality using id_values
        """
        self._validate_query_params(
            filters=filters, where=where, joins=None, order_by=None
        )

        # First confirm existence to return 404 if missing
        existing = await self.get_by_id(
            session=session,
            id_values=id_values,
            filters=filters,
            where=where,
        )
        if existing is None:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found"
            )

        # Build filters for UPDATE where clause
        if filters or where:
            # Rebuild SELECT to generate filters expressions
            built_filters: List[BinaryExpression] = []
            if filters:
                for column, value in filters.items():
                    built_filters.append(column == value)
            if where:
                for condition in where:
                    if isinstance(condition, BinaryExpression):
                        built_filters.append(condition)
                    elif isinstance(condition, ColumnElement):
                        # Bare column in where → treat as boolean truthy (rare), include as-is
                        built_filters.append(
                            condition.is_(True)
                        )  # conservative default
            filters_exprs = built_filters
        else:
            filters_exprs = self._pk_filters_from_values(id_values)

        updated = await self._do_update(
            session=session,
            filters_exprs=filters_exprs,
            data=data,
        )
        return updated  # type: ignore[return-value]

    async def upsert(
        self,
        session: AsyncSession,
        *,
        id_values: Optional[Union[Any, Dict[str, Any]]] = None,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        data: Dict[str, Any],
    ) -> ModelType:
        """
        Insert or update a record based on target selection.

        Target selection:
        - If filters/where provided → use them
        - Else → fallback to primary key equality using id_values
        """
        self._validate_query_params(
            filters=filters, where=where, joins=None, order_by=None
        )

        # Build selection statement
        if filters or where:
            base = select(self.model)
            stmt = self._apply_common_query_parts(
                base_select=base,
                filters=filters,
                where=where,
                joins=None,
                order_by=None,
            )
        else:
            pk_filters = self._pk_filters_from_values(id_values)
            stmt = select(self.model).where(*pk_filters)
            stmt = self._apply_soft_delete_filter(stmt)

        result = await self.execute(stmt=stmt, session=session)
        existing = result.scalars().first()

        if existing is not None:
            # Build filters for UPDATE
            if filters or where:
                built_filters: List[BinaryExpression] = []
                if filters:
                    for column, value in filters.items():
                        built_filters.append(column == value)
                if where:
                    for condition in where:
                        if isinstance(condition, BinaryExpression):
                            built_filters.append(condition)
                        elif isinstance(condition, ColumnElement):
                            built_filters.append(condition.is_(True))
                filters_exprs = built_filters
            else:
                filters_exprs = self._pk_filters_from_values(id_values)

            updated = await self._do_update(
                session=session,
                filters_exprs=filters_exprs,
                data=data,
            )
            return updated  # type: ignore[return-value]

        # Create path
        create_data = self._set_audit_fields(data)
        
        # Do NOT include PK if it's supposed to be generated by trigger
        pk_columns = self._pk_names()
        for pk in pk_columns:
            if pk in create_data and create_data[pk] is None:
                del create_data[pk]   # Remove null PK so trigger can generate it

        self._log_stmt(insert(self.model).values(**create_data), session)

        obj = self.model(**create_data)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(
        self,
        session: AsyncSession,
        *,
        id_values: Optional[Union[Any, Dict[str, Any]]] = None,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
        soft: bool = True,
    ) -> None:
        """
        Delete a record (soft-delete by default).

        Target selection:
        - If filters/where provided → use them
        - Else → fallback to primary key equality using id_values

        Soft-delete behavior:
        - If model supports deleted_ind or deleted_at/deleted_date, flips flags
        - Otherwise performs hard delete
        """
        self._validate_query_params(
            filters=filters, where=where, joins=None, order_by=None
        )

        obj = await self.get_by_id(
            session=session,
            id_values=id_values,
            filters=filters,
            where=where,
        )
        if obj is None:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found"
            )
        
        ctx = get_request_context()
        user_id = ctx.get("user_id")
        chamber_id = cast(str, ctx.get("chamber_id"))

        if soft and (
            hasattr(obj, "deleted_ind")
            or hasattr(obj, "deleted_at")
            or hasattr(obj, "deleted_date")
        ):
            if hasattr(obj, "deleted_ind"):
                obj.deleted_ind = True
            # Support common deleted fields
            now_utc = datetime.now(timezone.utc)
            if hasattr(obj, "deleted_at"):
                obj.deleted_at = now_utc
            if hasattr(obj, "deleted_date"):
                obj.deleted_date = now_utc
            if hasattr(obj, "deleted_by"):
                obj.deleted_by = user_id
            if hasattr(obj, "chamber_id"):
                obj.chamber_id = chamber_id
            session.add(obj)
        else:
            await session.delete(obj)

        await session.flush()

    async def undelete(
        self,
        session: AsyncSession,
        *,
        id_values: Optional[Union[Any, Dict[str, Any]]] = None,
        filters: Optional[Dict[FilterKey, Any]] = None,
        where: Optional[Sequence[Any]] = None,
    ) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        """
        self._validate_query_params(filters=filters, where=where)

        # Build filters
        if filters or where:
            built_filters: List[BinaryExpression] = []
            if filters:
                for column, value in filters.items():
                    built_filters.append(column == value)
            if where:
                built_filters.extend(where)
            filters_exprs = built_filters
        else:
            filters_exprs = self._pk_filters_from_values(id_values)

        update_data = {}

        # Reset soft delete flags
        if hasattr(self.model, "deleted_ind"):
            update_data["deleted_ind"] = False
        if hasattr(self.model, "deleted_date"):
            update_data["deleted_date"] = None
        if hasattr(self.model, "deleted_by"):
            update_data["deleted_by"] = None

        # Apply update directly (bypass soft-delete filter)
        stmt = (
            update(self.model)
            .where(*filters_exprs)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )

        await self.execute(stmt, session)

        # Reload using normal flow (now visible again)
        obj = await self.get_by_id(session=session, id_values=id_values)

        if obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} not found after undelete"
            )

        return obj

    @classmethod
    def get_bool_fields(cls, table: Table) -> set[str]:
        bool_fields = set()

        for col in table.c.values():
            # Native BOOLEAN
            if isinstance(col.type, Boolean):
                bool_fields.add(col.name)

            # MySQL BOOLEAN alias → TINYINT(1)
            elif (
                isinstance(col.type, TINYINT)
                and getattr(col.type, "display_width", None) == 1
            ):
                bool_fields.add(col.name)

        return bool_fields

    @classmethod
    async def get_all_refm_data(
        cls,
        *,
        session: AsyncSession,
        refm_models: List[Type[OrmModel]],
        exclude_fields: set[str] | None = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all rows from all Refm* tables dynamically.
        """
        exclude_fields = exclude_fields or {
            "id",
            "created_date",
            "created_by",
            "updated_date",
            "updated_by",
            "deleted_ind",
            "deleted_date",
            "deleted_by",
            "sort_order",
        }

        result: Dict[str, List[Dict[str, Any]]] = {}
        metadata = MetaData()

        conn = await session.connection()

        for model in sorted(refm_models, key=lambda m: m.__tablename__):
            table_name = model.__tablename__

            table = await conn.run_sync(
                lambda sync_conn: Table(
                    table_name,
                    metadata,
                    autoload_with=sync_conn,
                )
            )

            bool_fields = cls.get_bool_fields(table)
            stmt = select(table)
            # Ensure 'id' column exists before ordering
            if "id" in table.c:
                stmt = stmt.order_by(table.c.id)
            if "sort_order" in table.c:
                stmt = stmt.order_by(table.c.sort_order)
            records = await session.execute(stmt)
            print(f"  🔄 {table_name}")

            rows = records.mappings().all()
            result[table.name.upper()] = [
                {
                    k: (v == 1 if k in bool_fields and v is not None else v)
                    for k, v in row.items()
                    if k not in exclude_fields
                }
                for row in rows
            ]

        return result
