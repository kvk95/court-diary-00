# create_ui_defaults_constants.py
import os
import re
from typing import Dict, Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import DefaultClause

load_dotenv()

DB_ENGINE = os.getenv("DB_ENGINE")
if not DB_ENGINE:
    raise ValueError("DB_ENGINE environment variable is not set!")

engine = create_engine(DB_ENGINE)
inspector = inspect(engine)

# Where to write the React/TS defaults file
FRONTEND_OUTPUT_DIR = os.path.join(os.getcwd(), "..", "frontend", "src", "constants")
if not os.path.exists(FRONTEND_OUTPUT_DIR):
    os.makedirs(FRONTEND_OUTPUT_DIR)

OUTPUT_FILENAME = "dbDefaults.ts"


def normalize_default_value(raw: Any) -> str:
    """
    Convert SQLAlchemy reflected default / server_default into a TS literal.
    This is heuristic and may need tuning based on your DB. [web:19][web:46]
    """
    if raw is None:
        return "undefined"

    # DefaultClause
    if isinstance(raw, DefaultClause):
        raw = raw.arg

    val = str(raw).strip()

    # Strip surrounding quotes if present
    if (val.startswith("'") and val.endswith("'")) or (
        val.startswith('"') and val.endswith('"')
    ):
        inner = val[1:-1]
        return f'"{inner}"'

    upper = val.upper()

    # Numeric?
    if re.fullmatch(r"-?\d+", val):
        return val  # integer
    if re.fullmatch(r"-?\d+\.\d+", val):
        return val  # float

    # Boolean-like (we won't generate for non-number/string columns anyway,
    # but keep this just in case)
    if upper in ("TRUE", "FALSE"):
        return upper.lower()

    # Fallback: treat as string
    return f'"{val}"'


# Columns to always skip by name (upper-case compare)
SKIP_COLUMN_NAMES = {"IS_DELETED"}


def is_supported_column_type(col_type: Any) -> bool:
    """
    Only allow:
      - string-like: CHAR, VARCHAR, TEXT
      - numeric/int: INT, DECIMAL, NUMERIC, FLOAT, DOUBLE, REAL
    Skip everything else. [web:49]
    """
    t = str(col_type).upper()

    # Explicitly reject boolean-ish types
    if any(x in t for x in ["TINYINT(1)", " BOOLEAN", " BOOL"]):
        return False

    # String types
    if any(x in t for x in ["CHAR", "VARCHAR", "TEXT"]):
        return True

    # Numeric / int types
    if any(x in t for x in ["INT", "DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL"]):
        return True

    return False


def collect_defaults() -> Dict[str, str]:
    """
    Returns a dict of { CONST_NAME: ts_literal_value }.
    CONST_NAME is <TABLE>_<COLUMN> in upper snake case.
    Only uses columns with supported types. [web:49]
    """
    defaults: Dict[str, str] = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        for col in columns:
            col_name = col["name"]

            # Skip specific column names like IS_DELETED
            if col_name.upper() in SKIP_COLUMN_NAMES:
                continue

            # Skip unsupported data types
            if not is_supported_column_type(col["type"]):
                continue

            default = col.get("default", None)
            server_default = col.get("server_default", None)

            # Prefer server_default if present
            raw_default = server_default if server_default is not None else default
            if raw_default is None:
                continue

            const_name = f"{table_name}_{col_name}".upper()
            ts_value = normalize_default_value(raw_default)
            defaults[const_name] = ts_value

    return defaults


def generate_ts_defaults_file(defaults: Dict[str, str]) -> str:
    """
    Build the TS interface + constant string.
      interface DBDefaults { TABLE_COL: type; }
      export const DB_DEFAULTS: DBDefaults = { TABLE_COL: value, ... }
    """
    interface_lines = []
    for key, value in sorted(defaults.items()):
        # infer TS type from literal
        if value in ("true", "false"):
            ts_type = "boolean"
        elif value == "undefined":
            ts_type = "any"
        elif value.startswith('"') and value.endswith('"'):
            ts_type = "string"
        else:
            if re.fullmatch(r"-?\d+(\.\d+)?", value):
                ts_type = "number"
            else:
                ts_type = "any"

        interface_lines.append(f"  {key}: {ts_type};")

    interface_block = "\n".join(interface_lines)

    const_lines = []
    for key, value in sorted(defaults.items()):
        const_lines.append(f"  {key}: {value},")

    const_block = "\n".join(const_lines)

    ts_code = (
        "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.\n"
        "// Run create_ui_defaults_constants.py to regenerate.\n\n"
        "export interface DBDefaults {\n"
        f"{interface_block}\n"
        "}\n\n"
        "export const DB_DEFAULTS: DBDefaults = {\n"
        f"{const_block}\n"
        "};\n"
    )

    return ts_code


def generate_db_defaults_constants():
    defaults = collect_defaults()
    if not defaults:
        print("No suitable default or server_default values found on any columns.")
        return

    ts_code = generate_ts_defaults_file(defaults)
    out_path = os.path.join(FRONTEND_OUTPUT_DIR, OUTPUT_FILENAME)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(ts_code)

    print(f"Generated DB defaults constants at: {out_path}")


if __name__ == "__main__":
    generate_db_defaults_constants()
