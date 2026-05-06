# app/whatsapp/session_store.py
#
# In-memory session store for WhatsApp flows.
#
# ⚠️  PRODUCTION NOTE: This is process-local memory.
#     Sessions reset on every server restart / deploy.
#     Replace with Redis or DB-backed store before going live:
#
#       set()  → await redis.setex(phone, 3600, json.dumps(data))
#       get()  → json.loads(await redis.get(phone) or 'null')
#       clear()→ await redis.delete(phone)
#
#     The interface (get/set/clear) is stable — only this file changes.

sessions: dict[str, dict] = {}


# ── Core ─────────────────────────────────────────────────────────────────────

def get(phone: str) -> dict | None:
    return sessions.get(phone)


def set(phone: str, data: dict) -> None:
    sessions[phone] = data


def clear(phone: str) -> None:
    sessions.pop(phone, None)


# ── Search-result helpers ─────────────────────────────────────────────────────
#
# Flows that ask the user to "search then pick a number" store their result
# list in session["search_results"] as a list of plain dicts with at least:
#   { "case_id": str, "label": str }
#
# Example:
#   set_search_results(phone, [
#       {"case_id": "abc-123", "label": "WP/1234/2024 — Rajan vs State"},
#   ])
#   item = pick_search_result(phone, "1")   # → {"case_id": "abc-123", ...}

def set_search_results(phone: str, results: list[dict]) -> None:
    session = get(phone)
    if session is not None:
        session["search_results"] = results


def pick_search_result(phone: str, message: str) -> dict | None:
    """
    Parse 'message' as a 1-based index into the stored search_results list.
    Returns the chosen dict, or None if the input is invalid.
    """
    session = get(phone)
    if not session:
        return None
    results: list[dict] = session.get("search_results", [])
    try:
        idx = int(message.strip()) - 1
        if idx < 0:
            return None
        return results[idx]
    except (ValueError, IndexError):
        return None