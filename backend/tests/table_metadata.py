# create_model.py
import os
from dotenv import load_dotenv
from sqlalchemy import (
    MetaData,
    create_engine,
    Table,
)
from sqlalchemy.orm import declarative_base

# Load environment variables
load_dotenv()

DB_ENGINE = os.getenv("DB_ENGINE")
if not DB_ENGINE:
    raise ValueError("DB_ENGINE environment variable is not set!")

engine = create_engine(DB_ENGINE)
Base = declarative_base()
metadata = MetaData()

TABLE_NAME = "user_roles"


# Set 'autoload_with' to automatically load table definitions from the database
table = Table(TABLE_NAME, metadata, autoload_with=engine)

# Access column metadata
for column in table.columns:
    print(f"Column: {column.name}")
    print(f"  Type: {column.type}")
    print(f"  Nullable: {column.nullable}")
    # The 'default' attribute holds the Default object, its 'arg' is the value
    default_value = (
        column.default.arg if column.default and column.default.arg else None
    )
    print(f"  Default: {default_value}")
    server_default = column.server_default
    default_value = None
    if server_default is not None and server_default.arg is not None:
        default_value = str(server_default.arg).strip("'")  # normalize if needed
    print(f"  Default: {default_value}")
    print("-" * 20)
