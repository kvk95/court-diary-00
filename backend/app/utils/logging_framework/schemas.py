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
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    error: Optional[str] = None
    metadataz: Optional[DBCallLogMeta] = None


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
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    error_code: Optional[str] = None
    metadataz: Optional[ExceptionLogMeta] = None


class ActivityMetadata(BaseModel):
    changes: Optional[Dict[str, Any]] = None


class ActivityLogPayload(BaseModel):
    timestamp: str
    action: str
    actor_user_id: Optional[int] = None
    actor_company_id: Optional[int] = None
    target: Optional[str] = None
    metadataz: Optional[ActivityMetadata] = None
    ip_address: Optional[str] = None
