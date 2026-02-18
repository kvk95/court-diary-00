# create_model.py
import os
import re
from dotenv import load_dotenv
from sqlalchemy import (
    MetaData,
    create_engine,
    inspect,
    Table,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import declarative_base
from typing import Any
from datetime import date, datetime  # required for type evaluation inside generator
from create_repository import generate_repositories
from create_ui_constants_context import generate_constants_context

# Load environment variables
load_dotenv()

DB_ENGINE = os.getenv("DB_ENGINE")
if not DB_ENGINE:
    raise ValueError("DB_ENGINE environment variable is not set!")

engine = create_engine(DB_ENGINE)
Base = declarative_base()
metadata = MetaData()

# Output directory
MODEL_OUTPUT_DIR = os.path.join(os.getcwd(), "app", "database", "models")
if not os.path.exists(MODEL_OUTPUT_DIR):
    os.makedirs(MODEL_OUTPUT_DIR)


def generate_class_name(table_name: str) -> str:
    return "".join(word.capitalize() for word in table_name.split("_"))


def python_type_from_sqlalchemy(type_name: str) -> Any:
    """Map SQLAlchemy types to Python types for Mapped[type] annotations."""
    mapping = {
        "Integer": int,
        "BigInteger": int,
        "SmallInteger": int,
        "Boolean": bool,
        "String": str,
        "CHAR": str,
        "Text": str,
        "LONGTEXT": str,
        "Date": date,
        "DateTime": datetime,
        "TIMESTAMP": datetime,
        "Float": float,
        "DOUBLE": float,
        "Numeric": float,
        "JSON": Any,
    }
    return mapping.get(type_name, Any)


def get_sqlalchemy_type_info(column):
    """
    Returns: (type_name, length_or_arg)
    - type_name: str like "String", "Boolean", "Integer"
    - length_or_arg: int or None (for String/CHAR) or False
    """
    db_type = column.type
    type_str = str(db_type).upper()

    # ENUM
    if isinstance(db_type, SQLAlchemyEnum):
        return "Enum", False

    # VARCHAR(n)
    if m := re.match(r"VARCHAR\((\d+)\)", type_str):
        return "String", int(m.group(1))

    # CHAR(n)
    if m := re.match(r"CHAR\((\d+)\)", type_str):
        return "CHAR", int(m.group(1))

    # TEXT / LONGTEXT
    if "LONGTEXT" in type_str:
        return "LONGTEXT", False
    if "TEXT" in type_str:
        return "Text", False

    # TINYINT → ALWAYS Boolean (common MySQL convention)
    if "TINYINT" in type_str:
        return "Boolean", False

    # Standard types
    mappings = {
        "INTEGER": "Integer",
        "BIGINT": "BigInteger",
        "SMALLINT": "SmallInteger",
        "BOOLEAN": "Boolean",
        "BOOL": "Boolean",
        "DATE": "Date",
        "DATETIME": "DateTime",
        "TIMESTAMP": "DateTime",
        "FLOAT": "Float",
        "DOUBLE": "DOUBLE",
        "DECIMAL": "Numeric",
        "NUMERIC": "Numeric",
        "JSON": "JSON",
        "YEAR": "SmallInteger",
    }
    for key, value in mappings.items():
        if key in type_str:
            return value, False

    return None, False  # fallback


def generate_model_class(table):
    class_name = generate_class_name(table.name)

    # Import tracking
    sa_types = set()  # String, Integer, Boolean, etc.
    mysql_types = set()  # LONGTEXT
    has_enum = False
    has_relationship = False
    has_foreign_key = False
    need_date = False
    need_datetime = False

    # Timestamp mixin
    has_timestamps = {"created_date", "updated_date"} <= {c.name for c in table.columns}
    base_classes = "BaseModel, TimestampMixin" if has_timestamps else "BaseModel"

    columns_code = []
    relationships_code = []
    enum_classes = []

    for column in table.columns:
        if has_timestamps and column.name in ("created_date", "updated_date"):
            continue
        col_name = column.name
        nullable = column.nullable
        primary_key = column.primary_key
        autoincrement = getattr(column, "autoincrement", False)
        default = column.default
        server_default_value = None
        server_default = column.server_default
        if (
            server_default is not None
            and getattr(server_default, "arg", None) is not None
        ):
            try:
                server_default_value = str(server_default.arg).strip("'")
            except Exception:
                server_default_value = None

        fks = column.foreign_keys

        if fks:
            has_foreign_key = True
            has_relationship = True

        # Use server_default_value when default is None
        if default is None:
            if server_default_value is not None:
                default = server_default_value
            else:
                default = None  # Explicitly set default to None if both are absent

        # Get type info
        type_name, length_or_arg = get_sqlalchemy_type_info(column)

        # Determine Python annotation type
        safe_type_name = type_name or ""
        python_type = python_type_from_sqlalchemy(safe_type_name)

        base_name = getattr(python_type, "__name__", "Any")
        if nullable:
            python_type_str = f"Optional[{base_name}]"
        else:
            python_type_str = base_name

        # Track date/datetime import needs
        if base_name == "date":
            need_date = True
        if base_name == "datetime":
            need_datetime = True

        # ENUM handling
        if isinstance(column.type, SQLAlchemyEnum):
            has_enum = True
            # Better enum class name: applies_to → AppliesTo → CouponsAppliesToEnum
            clean_col_name = "".join(part.capitalize() for part in col_name.split("_"))
            enum_name = f"{class_name}{clean_col_name}Enum"

            enum_lines = []
            for value in column.type.enums:
                # Create valid identifier: remove spaces and camel-case properly
                member_name = "".join(part.capitalize() for part in value.split())
                enum_lines.append(f'    {member_name} = "{value}"')

            enum_body = "\n".join(enum_lines)
            enum_classes.append(f"class {enum_name}(PyEnum):\n{enum_body}\n")

            sa_types.add("Enum")
            col_type_str = f"Enum({enum_name})"
            python_type_str = enum_name

        else:
            if type_name == "LONGTEXT":
                mysql_types.add("LONGTEXT")
                col_type_str = "LONGTEXT"
            elif type_name:
                sa_types.add(type_name)
                if length_or_arg:
                    col_type_str = f"{type_name}({length_or_arg})"
                else:
                    col_type_str = type_name
            else:
                col_type_str = str(column.type)

        # Build column (mapped_column)
        field = f"    # {col_name} : {column.type}\n"
        field += (
            f"    {col_name}: Mapped[{python_type_str}] = mapped_column({col_type_str}"
        )

        if primary_key:
            field += ", primary_key=True"
            if type_name in ("Integer", "BigInteger"):
                field += f", autoincrement={autoincrement}"

        if fks:
            fk = list(fks)[0]
            target = f"{fk.column.table.name}.{fk.column.name}"
            fk_args = f'"{target}"'

            # Detect and add ondelete if explicitly defined in the constraint
            if fk.ondelete:
                ondelete_val = fk.ondelete.upper()
                if ondelete_val in {
                    "CASCADE",
                    "RESTRICT",
                    "SET NULL",
                    "NO ACTION",
                    "SET DEFAULT",
                }:
                    fk_args += f', ondelete="{ondelete_val}"'

            # if fk.onupdate:
            #     onupdate_val = fk.onupdate.upper()
            #     if onupdate_val in valid_actions:
            #         fk_args += f', onupdate="{onupdate_val}"'

            field += f", ForeignKey({fk_args})"

        if type_name == "Boolean":
            if default is None:
                field += ", default=False"
            elif default is not None:
                try:
                    field += f", default={bool(int(default))}"
                except Exception:
                    field += ", default=False"

        elif type_name in ["Date", "DateTime", "TIMESTAMP"] and default is not None:
            if type_name == "Date" and default == "(curdate())":
                field += ", server_default=func.curdate()"
            elif type_name in ["DateTime", "TIMESTAMP"]:
                field += ", server_default=func.current_timestamp()"

        elif type_name == "JSON":
            if default is not None:
                text_val = repr(default)
                clean = re.sub(r"^.*?\[(.*?)\].*$", r"\1", text_val)
                field += f", server_default=text('[{clean}]')"
            else:
                field += ", default=[]"

        elif default is not None:
            if type_name in ["Integer", "BigInteger"]:
                field += f", default={default}"
            else:
                field += f", default={repr(default)}"

        if not nullable:
            field += ", nullable=False"

        field += ")\n"
        columns_code.append(field)

        # Relationship
        if fks:
            fk = list(fks)[0]
            parent_class = generate_class_name(fk.column.table.name)
            # base_name = (
            #     col_name.removesuffix("_id").removesuffix("_code").removesuffix("_by")
            # )
            base_name = col_name
            target_col_name = fk.column.name
            rel_name = f"{table.name}_{base_name}_{fk.column.table.name}"
            backref_name = f"{rel_name}s"  # plural for collection on the other side

            relationships_code.append(
                f"    # {table.name}.{base_name} -> {fk.column.table.name}.{target_col_name}"
            )

            remote_side = (
                f", remote_side=[{fk.column.name}]"
                if fk.column.table.name == table.name
                else ""
            )

            rel_code = (
                f'    {rel_name} = relationship(\n        "{parent_class}",\n'
                f"        foreign_keys=[{col_name}]{remote_side}, "
            )
            rel_code += f'\n        backref=backref("{backref_name}", cascade="all, delete-orphan")\n    )\n'
            relationships_code.append(rel_code)

    # === Build clean sorted imports ===
    imports = []

    core = []
    if has_foreign_key:
        core.append("ForeignKey")
    if sa_types:
        core.extend(sorted(sa_types))

    if core:
        imports.append(f"from sqlalchemy import {', '.join(core)}")

    if mysql_types:
        imports.append(
            f"from sqlalchemy.dialects.mysql import {', '.join(sorted(mysql_types))}"
        )

    if has_enum:
        imports.append("from enum import Enum as PyEnum")

    if has_relationship:
        imports.append("from sqlalchemy.orm import relationship, backref")

    imports.append("from sqlalchemy.orm import Mapped, mapped_column")
    imports.append("from sqlalchemy.sql import func, text")

    # Conditional datetime/date imports
    if need_date and need_datetime:
        imports.append("from datetime import date, datetime")
    elif need_date:
        imports.append("from datetime import date")
    elif need_datetime:
        imports.append("from datetime import datetime")

    imports.append("from typing import Any, Optional")
    imports.append("")
    imports.append("from app.database.models.base.base_model import BaseModel")
    if has_timestamps:
        imports.append(
            "from app.database.models.base.timestampmixin import TimestampMixin"
        )

    # === Final code ===
    code = "\n".join(imports) + "\n\n"

    if enum_classes:
        code += "\n".join(enum_classes) + "\n"

    code += f"class {class_name}({base_classes}):\n"
    code += f"    __tablename__ = '{table.name}'\n\n"

    code += "\n".join(columns_code)
    if columns_code:
        code += "\n"

    code += (
        "    # FORWARD RELATIONSHIPS "
        + "-" * 60
        + "\n    # A forward relationship is defined in the table that contains the foreign key.\n\n"
    )

    if relationships_code:
        code += "\n".join(relationships_code) + "\n"
    else:
        code += "    #    -- No relationships defined. --\n\n"

    code += "    # FORWARD RELATIONSHIPS " + "-" * 60 + "\n\n"

    # >>> START APPEND CONSTANTS CLASS <<<

    constants_class_code = ""
    if table.name.startswith("refm_"):
        # Fetch rows from this refm_* table to build constants
        try:
            with engine.connect() as conn:
                if "sort_order" in table.c:
                    stmt = table.select().order_by(table.c.sort_order)
                else:
                    stmt = table.select()
                result = conn.execute(stmt)
                rows = result.fetchall()

                if rows and all(hasattr(r, "code") for r in rows):
                    constants_lines = []
                    for row in rows:
                        # Prefer 'name', fallback to 'description'
                        raw_key = getattr(
                            row, "name", getattr(row, "description", None)
                        )
                        if raw_key is None:
                            continue
                        # Clean key to be a valid Python identifier: uppercase, replace non-alnum with _
                        key = re.sub(
                            r"\s+",
                            "_",
                            re.sub(
                                r"[^A-Za-z0-9_\s]",
                                " ",
                                re.sub(r"[^\x00-\x7F]", "", str(raw_key)),
                            )
                            .strip()
                            .upper(),
                        )
                        # Ensure it starts with a letter or underscore
                        if key[0].isdigit():
                            key = "_" + key
                        value = row.code
                        constants_lines.append(f"    {key} = {repr(value)}")

                    if constants_lines:
                        refm_class_name = (
                            "Refm"
                            + "".join(
                                part.capitalize() for part in table.name[5:].split("_")
                            )
                            + "Constants"
                        )
                        constants_class_code = (
                            f"\nclass {refm_class_name}:\n"
                            + "\n".join(constants_lines)
                            + "\n"
                        )
        except Exception:
            # If data access fails (e.g., during CI), skip gracefully
            pass

    if constants_class_code:
        code += constants_class_code
    # <<< END APPEND CONSTANTS CLASS >>>

    return f'"""{table.name}"""\n\n' + code


def generate_models():
    # Clean old models
    for filename in os.listdir(MODEL_OUTPUT_DIR):
        if filename not in [
            "base_model.py",
            "__init__.py",
            "timestampmixin.py",
            "base.py",
        ]:
            path = os.path.join(MODEL_OUTPUT_DIR, filename)
            if os.path.isfile(path):
                os.remove(path)

    metadata.reflect(bind=engine)
    inspector = inspect(engine)

    print("\n\n⏳Generating models...")
    for table_name in inspector.get_table_names():
        table = Table(table_name, metadata, autoload_with=engine)
        code = generate_model_class(table)
        filepath = os.path.join(MODEL_OUTPUT_DIR, f"{table_name}.py")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"🆗 Generated: {table_name}.py")

    print("✅ All models generated successfully!\n\n")


if __name__ == "__main__":
    generate_models()

    generate_repositories()
    generate_constants_context()
