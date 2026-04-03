from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class DBCallLogParams(BaseModel):
    values: Optional[Dict[str, Any]] = None


class DBCallLogMeta(BaseModel):
    details: Optional[Dict[str, Any]] = None


class DBCallLogPayload(BaseModel):
    timestamp: str
    duration_ms: float
    raw_query: str
    params: Optional[DBCallLogParams] = None
    final_query: Optional[str] = None
    repo: Optional[str] = None
    error: Optional[str] = None
    metadata_json: Optional[DBCallLogMeta] = None


class ExceptionHeaders(BaseModel):
    headers: Optional[Dict[str, Any]] = None


class ExceptionQueryParams(BaseModel):
    params: Optional[Dict[str, Any]] = None


class ExceptionLogMeta(BaseModel):
    details: Optional[Dict[str, Any]] = None


class ExceptionLogPayload(BaseModel):
    timestamp: str
    exception_type: str
    message: Optional[str] = None
    stacktrace: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    query_params: Optional[ExceptionQueryParams] = None
    request_body: Optional[str] = None
    headers: Optional[ExceptionHeaders] = None
    user_id: Optional[str] = None
    company_id: Optional[int] = None
    error_code: Optional[str] = None
    metadataz: Optional[ExceptionLogMeta] = None


class ActivityMetadata(BaseModel):
    changes: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class ActivityLogPayload(BaseModel):
    action: str    
    target: Optional[str] = None
    metadata_json: Optional[ActivityMetadata] = None
    timestamp: datetime
    actor_user_id: Optional[str] = None
    actor_chamber_id: Optional[int] = None
    ip_address: Optional[str] = None
