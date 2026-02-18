# generate_single_table_crud.py
import os
from sqlalchemy import create_engine, Table, MetaData
from dotenv import load_dotenv
import re

load_dotenv()

DB_ENGINE = os.getenv("DB_ENGINE")
if not DB_ENGINE:
    raise ValueError("DB_ENGINE environment variable is not set!")

engine = create_engine(DB_ENGINE)
metadata = MetaData()


def to_pascal_case(s: str) -> str:
    """snake_case → PascalCase"""
    return "".join(word.capitalize() for word in re.split(r"[_-]", s))


def to_camel_case(s: str) -> str:
    """snake_case → camelCase"""
    parts = re.split(r"[_-]", s)
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def get_primary_key(table: Table):
    for col in table.columns:
        if col.primary_key:
            return col.name
    return f"{table.name}_id"


def python_type_str(col_type: str, nullable: bool) -> str:
    mapping = {
        "INT": "int",
        "BIGINT": "int",
        "SMALLINT": "int",
        "TINYINT": "bool",
        "BOOLEAN": "bool",
        "VARCHAR": "str",
        "CHAR": "str",
        "TEXT": "str",
        "LONGTEXT": "str",
        "DATE": "date",
        "DATETIME": "datetime",
        "TIMESTAMP": "datetime",
        "FLOAT": "float",
        "DOUBLE": "float",
        "DECIMAL": "float",
        "NUMERIC": "float",
        "JSON": "Any",
    }
    base = "Any"
    for key, val in mapping.items():
        if key in col_type.upper():
            base = val
            break
    if nullable and base not in ("Any",):
        return f"Optional[{base}] = None"
    return base


def generate_crud_for_table(table_name: str):
    try:
        metadata.reflect(bind=engine, only=[table_name])
        if table_name not in metadata.tables:
            print(f"ERROR: Table '{table_name}' not found!")
            return

        table = metadata.tables[table_name]
        pascal = to_pascal_case(table_name)
        camel = to_camel_case(table_name)
        pk_col = get_primary_key(table)
        out_dto = f"{pascal}Out"
        create_in = f"{pascal}CreateIn"
        update_in = f"{pascal}UpdateIn"
        delete_in = f"{pascal}DeleteIn"

        status_field = (
            "status_ind" if "status" in [c.name for c in table.columns] else "status"
        )

        print("\n" + "=" * 100)
        print(f"  FULL CRUD GENERATION FOR TABLE: {table_name} (Coupons Pattern)")
        print(f"  Model: {pascal} | PK: {pk_col} | Status Field: {status_field}")
        print("=" * 100 + "\n")

        # ==================== 1. DTOs ====================
        print(f"1. DTOs → app/dtos/{table_name}_dtos.py")
        print("-" * 80)

        out_fields = []
        create_fields = []
        need_date = False
        need_datetime = False
        need_any = False

        for col in table.columns:
            if col.name in (
                "created_date",
                "updated_date",
                "created_by",
                "updated_by",
                "deleted_by",
                "is_deleted",
                "company_id",
                "password",
            ):
                continue

            py_type = python_type_str(str(col.type), col.nullable)
            if "date" in py_type and "Optional" not in py_type:
                need_date = True
            if "datetime" in py_type:
                need_datetime = True
            if "Any" in py_type:
                need_any = True

            field_line = f"    {col.name}: {py_type}"
            if col.name == "email":
                field_line = (
                    "    email: EmailStr"
                    if not col.nullable
                    else "    email: Optional[EmailStr] = None"
                )

            out_fields.append(field_line)

            if not col.primary_key:
                create_line = (
                    field_line.replace(" | None = None", "")
                    .replace("Optional[", "")
                    .replace("] = None", "")
                )
                if col.name == "email":
                    create_line = "    email: EmailStr"
                create_fields.append(create_line)

        imports = [
            "from datetime import date" if need_date else "",
            (
                "from typing import Any, Optional"
                if need_any or any("Optional" in f for f in out_fields)
                else "from typing import Optional"
            ),
            "from app.dtos.base.base_in_data import BaseInData",
            "from pydantic import EmailStr",
        ]
        imports = [i for i in imports if i]

        if need_date and need_datetime:
            imports.insert(0, "from datetime import date, datetime")

        print("\n".join(imports))
        print(f"\nclass {out_dto}(BaseInData):")
        print("\n".join(out_fields) if out_fields else "    pass")

        print(f"\nclass {create_in}(BaseInData):")
        print("\n".join(create_fields) if create_fields else "    pass")

        print(f"\nclass {update_in}({create_in}):")
        print(f"    {pk_col}: int  # Only extra field needed")

        print(f"\nclass {delete_in}(BaseInData):")
        print(f"    {pk_col}: int  # Minimal for delete")
        print("\n" + "-" * 80 + "\n")

        # ==================== 2. REPOSITORY ====================
        print(f"2. REPOSITORY → app/database/repositories/{table_name}_repository.py")
        print("-" * 80)
        repo_code = f"""from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logging_framework.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.{table_name} import {pascal}
from app.dtos.{table_name}_dtos import {out_dto}

@apply_repo_context
class {pascal}Repository(BaseRepository[{pascal}]):
    def __init__(self):
        super().__init__({pascal})

    async def {table_name}_list_paginated(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        company_id: int,
        search: Optional[str] = None,
        {status_field}: Optional[bool] = None,
    ) -> Tuple[List[{out_dto}], int]:
        stmt = select({pascal}).where(
            and_(
                {pascal}.is_deleted.is_(False),
                {pascal}.company_id == company_id,
            )
        )

        if search:
            search_pattern = f"%{{search}}%"
            conditions = []
            if hasattr({pascal}, "email"):
                conditions.append({pascal}.email.ilike(search_pattern))
            if hasattr({pascal}, "name"):
                conditions.append({pascal}.name.ilike(search_pattern))
            if conditions:
                stmt = stmt.where(or_(*conditions))

        if {status_field} is not None:
            stmt = stmt.where({pascal}.{status_field} == {status_field})

        total = (
            await session.execute(stmt.with_only_columns(func.count()).order_by(None))
        ).scalar_one()

        order_by = [{pascal}.{status_field}.desc()]
        if hasattr({pascal}, "name"):
            order_by.append({pascal}.name.asc())
        else:
            order_by.append({pascal}.{pk_col}.desc())

        stmt = stmt.order_by(*order_by).offset((page - 1) * limit).limit(limit)
        result = await session.execute(stmt)
        records = result.scalars().all()
        dtos = [{out_dto}.model_validate(rec) for rec in records]
        return dtos, total
"""
        print(repo_code)
        print("-" * 80 + "\n")

        # ==================== 3. SERVICE ====================
        print(f"3. SERVICE → app/services/{table_name}_service.py")
        print("-" * 80)
        service_code = f"""from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.dtos.oauth_dtos import CurrentUserContext
from app.database.repositories.{table_name}_repository import {pascal}Repository
from app.dtos.base.paginated_out import PagingBuilder, PagingData
from app.dtos.{table_name}_dtos import {out_dto}, {create_in}, {update_in}, {delete_in}
from app.services.base.secured_base_service import BaseSecuredService

class {pascal}Service(BaseSecuredService):
    def __init__(
        self,
        session: AsyncSession,
        current_user: CurrentUserContext,
        {camel}_repo: {pascal}Repository | None = None,
    ):
        super().__init__(session, current_user)
        self.{camel}_repo = {camel}_repo or {pascal}Repository()

    async def {table_name}_get_paged(
        self,
        page: int,
        limit: int,
        search: Optional[str] | None = None,
        {status_field}: Optional[bool] | None = None,
    ) -> PagingData[{out_dto}]:
        records, total = await self.{camel}_repo.{table_name}_list_paginated(
            session=self.session,
            page=page,
            limit=limit,
            company_id=self.company_id,
            search=search,
            {status_field}={status_field},
        )
        builder = PagingBuilder(total_records=total, page=page, limit=limit)
        return builder.build(records=records)

    async def {table_name}_create(self, payload: {create_in}) -> int:
        data = payload.model_dump()
        data["company_id"] = self.company_id
        obj = await self.{camel}_repo.create(
            session=self.session,
            data=data,
            created_by=self.user_id,
        )
        return obj.{pk_col}

    async def {table_name}_update(self, payload: {update_in}) -> int:
        data = payload.model_dump()
        data["company_id"] = self.company_id
        obj = await self.{camel}_repo.update(
            session=self.session,
            filters={{
                self.{camel}_repo.model.{pk_col}: payload.{pk_col},
                self.{camel}_repo.model.company_id: self.company_id,
            }},
            data=data,
            updated_by=self.user_id,
        )
        return obj.{pk_col}

    async def {table_name}_delete(self, payload: {delete_in}) -> bool:
        await self.{camel}_repo.delete(
            session=self.session,
            filters={{
                self.{camel}_repo.model.{pk_col}: payload.{pk_col},
                self.{camel}_repo.model.company_id: self.company_id,
            }},
            deleted_by=self.user_id,
            soft=True,
        )
        return True
"""
        print(service_code)
        print("-" * 80 + "\n")

        # ==================== 4. CONTROLLER ====================
        print(f"4. CONTROLLER → app/api/v1/routes/{table_name}_controller.py")
        print("-" * 80)
        controller_code = f"""from __future__ import annotations
from fastapi import Body, Depends, Query
from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_{table_name}_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.base.paginated_out import PagingData
from app.dtos.{table_name}_dtos import (
    {out_dto},
    {create_in},
    {update_in},
    {delete_in},
)
from app.services.{table_name}_service import {pascal}Service
from app.utils.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_PAGE

class {pascal}Controller(BaseController):
    @BaseController.get(
        "/{table_name}/paged",
        summary="Get {pascal} (paginated)",
        response_model=BaseOutDto[PagingData[{out_dto}]],
    )
    async def {table_name}_get_paged(
        self,
        page: int = Query(PAGINATION_DEFAULT_PAGE, ge=1, le=10_000),
        limit: int = Query(PAGINATION_DEFAULT_LIMIT, ge=1, le=1000),
        search: str | None = Query(None),
        {status_field}: bool | None = Query(None),
        service: {pascal}Service = Depends(get_{table_name}_service),
    ) -> BaseOutDto[PagingData[{out_dto}]]:
        result = await service.{table_name}_get_paged(page, limit, search, {status_field})
        return self.success(result=result)

    @BaseController.post(
        "/{table_name}/add",
        summary="{pascal} - Add new",
        response_model=BaseOutDto[int],
    )
    async def {table_name}_create(
        self,
        payload: {create_in} = Body(..., description="Add new {pascal}"),
        service: {pascal}Service = Depends(get_{table_name}_service),
    ) -> BaseOutDto[int]:
        result = await service.{table_name}_create(payload)
        return self.success(result=result)

    @BaseController.put(
        "/{table_name}/edit",
        summary="{pascal} - Update",
        response_model=BaseOutDto[int],
    )
    async def {table_name}_update(
        self,
        payload: {update_in} = Body(..., description="Update {pascal} (include {pk_col})"),
        service: {pascal}Service = Depends(get_{table_name}_service),
    ) -> BaseOutDto[int]:
        result = await service.{table_name}_update(payload)
        return self.success(result=result)

    @BaseController.delete(
        "/{table_name}/delete",
        summary="{pascal} - Delete",
        response_model=BaseOutDto[bool],
    )
    async def {table_name}_delete(
        self,
        payload: {delete_in} = Body(..., embed=True),
        service: {pascal}Service = Depends(get_{table_name}_service),
    ) -> BaseOutDto[bool]:
        result = await service.{table_name}_delete(payload)
        return self.success(result=result)
"""
        print(controller_code)
        print("\n" + "=" * 100)
        print("GENERATION COMPLETE! (Coupons/Promotions Pattern)")
        print("Next steps:")
        print("  • Add get_{table_name}_service dependency")
        print("  • Register controller in router")
        print("  • Ensure @apply_repo_context is available")
        print("=" * 100)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    table = "invoices"
    generate_crud_for_table(table)
