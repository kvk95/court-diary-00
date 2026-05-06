# app/whatsapp/refm_cache.py
#
# Fetches /api/anonymous/refm ONCE at app startup and caches only what
# the WhatsApp flows need. Zero runtime HTTP calls after that.
#
# Usage:
#   from app.whatsapp.refm_cache import refm_cache
#   purposes = refm_cache.hearing_purposes   # list[dict]  {code, description}
#   statuses  = refm_cache.case_statuses
#
# Boot:
#   In your FastAPI lifespan / startup event:
#       await refm_cache.load(base_url="https://your-api.example.com")

import logging

from app.database.models.cases import Cases
from app.database.models.hearings import Hearings
from app.database.models.refm_case_status import RefmCaseStatus
from app.database.models.refm_hearing_purpose import RefmHearingPurpose
from app.database.models.refm_hearing_status import RefmHearingStatus, RefmHearingStatusConstants
from app.utils.refm.refm_resolver import RefmResolver

logger = logging.getLogger(__name__)

CASE_STATUSES_MAP = None


class WRefmCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WRefmCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # Cached data
        self.hearing_purposes: list[dict] = []
        self.case_statuses: list[dict] = []
        self.hearing_statuses: list[dict] = []

        self._loaded = False

    async def load(self, session):
        if self._loaded:
            return

        resolver = RefmResolver(session=session)

        hearing_purpose_map  = await resolver.get_desc_map(
            column_attr=Hearings.purpose_code,
            value_column=RefmHearingPurpose.description
        )

        case_status_map = await resolver.get_desc_map(
            column_attr=Cases.status_code,
            value_column=RefmCaseStatus.description
        )

        hearing_status_map = await resolver.get_desc_map(
            column_attr=Hearings.status_code,
            value_column=RefmHearingStatus.description
        )

        # 🔥 Convert dict → list[dict]
        self.hearing_purposes = [
            {"code": code, "description": desc}
            for code, desc in hearing_purpose_map.items()
        ]

        self.case_statuses = [
            {"code": code, "description": desc}
            for code, desc in case_status_map.items()
        ]

        self.hearing_statuses = [
            {"code": code, "description": desc}
            for code, desc in hearing_status_map.items()
        ]

        self._loaded = True

    def format_hearing_purpose_menu(self) -> str:
        if not self.hearing_purposes:
            return ""

        lines = ["📌 Purpose (or type SKIP):\n"]
        for i, p in enumerate(self.hearing_purposes, 1):
            lines.append(f"{i}. {p['description']}")
        return "\n".join(lines)
    
    def format_case_status_menu(self, current_code: str | None = None) -> str:
        if not self.case_statuses:
            return ""

        lines = ["📋 Select new status:\n"]
        for i, s in enumerate(self.case_statuses, 1):
            marker = " ◀ current" if s["code"] == current_code else ""
            lines.append(f"{i}. {s['description']}{marker}")
        return "\n".join(lines)
    
    def pick_hearing_purpose(self, message: str) -> dict | None:
        try:
            return self.hearing_purposes[int(message) - 1]
        except (ValueError, IndexError):
            return None

    def pick_case_status(self, message: str) -> dict | None:
        try:
            return self.case_statuses[int(message) - 1]
        except (ValueError, IndexError):
            return None
        
    @property
    def default_hearing_status_code(self) -> str:
        for s in self.hearing_statuses:
            if s["code"] == RefmHearingStatusConstants.UPCOMING:
                return RefmHearingStatusConstants.UPCOMING

        return self.hearing_statuses[0]["code"] if self.hearing_statuses else RefmHearingStatusConstants.UPCOMING
    
wrefm_cache_instance = WRefmCache()