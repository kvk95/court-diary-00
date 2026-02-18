# app\utils\logging_framework\log_types.py

from enum import Enum


class LogType(str, Enum):
    HTTP_LOG   = "http_log"
    DB_CALL    = "db_call"
    EXCEPTION  = "exception"
    ACTIVITY   = "activity"
