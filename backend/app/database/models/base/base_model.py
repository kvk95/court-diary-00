# app\database\models\base\base_model.py
import json
from typing import Any, Dict
from uuid6 import uuid7
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    # Pylance-approved: subclasses assign a string
    __tablename__: str

    @staticmethod
    def generate_uuid() -> str:
        """Application-level UUID v7 generator (consistent with DB)."""
        return str(uuid7())

    def __repr__(self):
        cls = self.__class__.__name__
        fields_as_json = json.dumps(self.__dict__, default=str, indent=4)
        return f"<{cls} {fields_as_json}>"

    @classmethod
    def get_table_name(cls):
        return cls.__tablename__
    
    def to_dict(
        self,
        *,
        exclude_none: bool = False,
        exclude: set[str] | None = None,
    ) -> Dict[str, Any]:
        exclude = exclude or set()
        out: Dict[str, Any] = {}

        for col in self.__table__.columns:
            key = col.name

            if key in exclude:
                continue

            val = getattr(self, key)

            if exclude_none and val is None:
                continue

            out[key] = val.isoformat() if hasattr(val, "isoformat") else val

        return out 
