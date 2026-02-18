import json
from typing import Any, Dict
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    # Pylance-approved: subclasses assign a string
    __tablename__: str

    def __repr__(self):
        cls = self.__class__.__name__
        fields_as_json = json.dumps(self.__dict__, default=str, indent=4)
        return f"<{cls} {fields_as_json}>"

    @classmethod
    def get_table_name(cls):
        return cls.__tablename__

    @classmethod
    def to_dict(cls, self) -> Dict[str, Any]:
        out = {}
        for col in cls.__table__.columns:
            val = getattr(self, col.name)
            out[col.name] = val.isoformat() if hasattr(val, "isoformat") else val
        return out
