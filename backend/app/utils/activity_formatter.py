"""activity_formatter.py — Human-readable activity log formatting"""

from typing import Any, Dict, Optional, Callable
from app.dtos.cases_dto import RecentActivityItem


def format_activity(log: Any, actor_name: Optional[str] = None) -> RecentActivityItem:
    """Format an ActivityLog entry into a RecentActivityItem DTO."""
    action = str(log.action or "").upper()
    metadata: Dict[str, Any] = log.metadata_json or {}

    base = {
        "action": log.action,
        "actor_name": actor_name or "System",
        "timestamp": getattr(log, "created_date", None) or getattr(log, "timestamp", None),
    }

    # Registry: map action suffix → formatter function
    handlers: Dict[str, Callable] = {
        "CREATED": _format_create,
        "UPDATED": _format_update,
        "DELETED": _format_delete,
        "STATUS_CHANGED": _format_status_change,
        "ASSIGNED": _format_assignment,
        "COMMENTED": _format_comment,
        "LINKED": _format_link,
        "UNLINKED": _format_unlink,
        "RESOLVED": _format_resolve,
        "REOPENED": _format_reopen,
    }

    # Find matching handler by suffix
    formatter = None
    for suffix, func in handlers.items():
        if action.endswith(suffix):
            formatter = func
            break

    if formatter:
        return formatter(base, metadata, action)

    # Fallback for unknown actions
    return RecentActivityItem(
        **base,
        title=action.replace("_", " ").title(),
        description=metadata.get("description") or "Activity recorded",
        type="INFO",
        icon="activity",
    )


def humanize_field(field: str) -> str:
    """Convert snake_case to readable Title Case"""
    return field.replace("_", " ").title()


def _get_entity_type(action: str) -> str:
    """Extract entity type from action (e.g., CASE, TICKET, NOTE)"""
    if "TICKET" in action:
        return "Ticket"
    if "NOTE" in action:
        return "Note"
    if "HEARING" in action:
        return "Hearing"
    if "CLIENT" in action:
        return "Client"
    return "Case"


# ─────────────────────────────────────────────────────────────────────
# FORMATTER IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────────

def _format_create(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    entity = _get_entity_type(action)
    return RecentActivityItem(
        **base,
        title=f"{entity} Created",
        description=metadata.get("description") or f"New {entity.lower()} was registered",
        type="CREATE",
        icon="plus-circle",
    )


def _format_delete(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    entity = _get_entity_type(action)
    return RecentActivityItem(
        **base,
        title=f"{entity} Deleted",
        description=metadata.get("description") or f"{entity} was deleted",
        type="DELETE",
        icon="trash-2",
    )


def _format_update(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    """Handles both legacy `changes` format and new `updated_fields` format."""
    entity = _get_entity_type(action)
    
    # Support legacy diff format if provided
    changes = metadata.get("changes", {})
    if changes:
        parts = []
        for field, diff in list(changes.items())[:4]:
            old = diff.get("old")
            new = diff.get("new")
            if old is None and new is not None:
                parts.append(f"{humanize_field(field)} set to '{new}'")
            elif old is not None and new is None:
                parts.append(f"{humanize_field(field)} was removed")
            else:
                parts.append(f"{humanize_field(field)} changed from '{old}' to '{new}'")
        
        desc = ", ".join(parts)
        if len(changes) > 4:
            desc += f" and {len(changes) - 4} more changes"
    else:
        # Fallback to `updated_fields` from _log_entity_change
        updated_fields = metadata.get("updated_fields", [])
        parts = []
        for field in updated_fields[:4]:
            val = metadata.get(field)
            if val is not None:
                parts.append(f"{humanize_field(field)} set to '{val}'")
            else:
                parts.append(f"{humanize_field(field)} was modified")
        desc = ", ".join(parts) if parts else (metadata.get("description") or f"{entity} details were updated")
        if len(updated_fields) > 4:
            desc += f" and {len(updated_fields) - 4} more changes"

    return RecentActivityItem(
        **base,
        title=f"{entity} Updated",
        description=desc,
        type="UPDATE",
        icon="edit-3",
    )


def _format_status_change(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    old_status = metadata.get("old_status_name") or metadata.get("old_status")
    new_status = metadata.get("new_status_name") or metadata.get("new_status")

    if old_status and new_status:
        desc = f"Status changed from **{old_status}** to **{new_status}**"
    else:
        desc = metadata.get("description") or "Status was updated"

    return RecentActivityItem(
        **base,
        title="Status Changed",
        description=desc,
        type="STATUS",
        icon="arrow-right-circle",
    )


def _format_assignment(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    assigned_to = metadata.get("assigned_to_name") or metadata.get("assigned_to")
    previous = metadata.get("previous_assignee_name")

    if previous and assigned_to:
        desc = f"Reassigned from {previous} to {assigned_to}"
    elif assigned_to:
        desc = f"Assigned to {assigned_to}"
    else:
        desc = "Assigned to a user"

    return RecentActivityItem(
        **base,
        title="Assigned",
        description=desc,
        type="ASSIGN",
        icon="user-check",
    )


def _format_comment(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    comment_preview = metadata.get("comment_preview", "")
    if comment_preview and len(comment_preview) > 85:
        comment_preview = comment_preview[:82] + "..."

    return RecentActivityItem(
        **base,
        title="New Comment",
        description=comment_preview or "Comment added",
        type="COMMENT",
        icon="message-square",
    )


def _format_link(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    relationship = metadata.get("relationship") or metadata.get("entity_type", "").upper()
    child_name = metadata.get("child_name") or metadata.get("client_id") or metadata.get("entity_id", "")

    if relationship == "CASE_CLIENT" or "CLIENT" in relationship:
        return RecentActivityItem(
            **base,
            title="Client Added",
            description=f"Client {child_name} linked",
            type="LINK",
            icon="user-plus",
        )

    return RecentActivityItem(
        **base,
        title="Linked",
        description=metadata.get("description") or "Entity linked",
        type="LINK",
        icon="link",
    )


def _format_unlink(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    relationship = metadata.get("relationship") or metadata.get("entity_type", "").upper()
    child_name = metadata.get("child_name") or metadata.get("client_id") or metadata.get("entity_id", "")

    if relationship == "CASE_CLIENT" or "CLIENT" in relationship:
        return RecentActivityItem(
            **base,
            title="Client Removed",
            description=f"Client {child_name} unlinked",
            type="UNLINK",
            icon="user-minus",
        )

    return RecentActivityItem(
        **base,
        title="Unlinked",
        description=metadata.get("description") or "Entity unlinked",
        type="UNLINK",
        icon="unlink",
    )


def _format_resolve(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    """Support Ticket specific"""
    return RecentActivityItem(
        **base,
        title="Ticket Resolved",
        description=metadata.get("description") or "Ticket marked as resolved",
        type="STATUS",
        icon="check-circle",
    )


def _format_reopen(base: dict, metadata: dict, action: str) -> RecentActivityItem:
    """Support Ticket specific"""
    return RecentActivityItem(
        **base,
        title="Ticket Reopened",
        description=metadata.get("description") or "Ticket reopened for further action",
        type="STATUS",
        icon="refresh-cw",
    )