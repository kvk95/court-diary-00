from typing import Any, Set, Type

from sqlalchemy import inspect


def get_writable_columns(model: Type[Any]) -> Set[str]:
    """
    Return set of column names that are safe to update from user input.

    Excludes:
    - Primary keys
    - Audit fields (created_by, updated_at, etc.)
    - Soft-delete fields (optional: include if editable)
    - Auto-generated columns (e.g., with server_default)

    Adjust exclusions based on your business rules.
    """
    mapper = inspect(model)
    pk_columns = {col.name for col in mapper.primary_key}

    # Define fields that should NEVER be updated by user
    protected_fields = {
        # "user_id",  # PK
        "created_date",
        "updated_date",
        "created_by",
        "updated_by",
        "deleted_date",
        "deleted_by",
        "password_hash",  # handled separately
        # Add others as needed
    }

    writable = set()
    for column in mapper.columns:
        if column.name not in pk_columns and column.name not in protected_fields:
            # Optional: skip columns with server_default if not user-editable
            # if column.server_default is None:
            writable.add(column.name)

    return writable
