from app.dtos.cases_dto import RecentActivityItem


def format_activity(log, actor_name: str | None):
    action = log.action
    metadata = log.metadata or {}

    base = {
        "action": action,
        "actor_name": actor_name,
        "timestamp": log.created_date,
    }

    if action.endswith("_CREATED"):
        return RecentActivityItem(
            **base,
            title="Created",
            description="New record created",
            type="CREATE",
            icon="plus",
        )

    if action.endswith("_DELETED"):
        return RecentActivityItem(
            **base,
            title="Deleted",
            description="Record removed",
            type="DELETE",
            icon="trash",
        )

    if action.endswith("_UPDATED"):
        return _format_update(base, metadata)

    if action.endswith("_LINKED"):
        return _format_link(base, metadata)

    if action.endswith("_UNLINKED"):
        return _format_unlink(base, metadata)

    return RecentActivityItem(**base)

def humanize_field(field: str) -> str:
    return field.replace("_", " ").title()

def _format_update(base, metadata):
    changes = metadata.get("changes", {})

    if not changes:
        return RecentActivityItem(
            **base,
            title="Updated",
            description="Details updated",
            type="UPDATE",
            icon="edit",
        )

    parts = []
    for field, val in changes.items():
        old = val.get("old")
        new = val.get("new")

        parts.append(
            f"{humanize_field(field)} changed from '{old}' to '{new}'"
        )

    return RecentActivityItem(
        **base,
        title="Updated details",
        description=", ".join(parts),
        type="UPDATE",
        icon="edit",
    )

def _format_link(base, metadata):
    relationship = metadata.get("relationship")

    if relationship == "CASE_CLIENT":
        return RecentActivityItem(
            **base,
            title="Client added",
            description=f"Client {metadata.get('child_id')} linked",
            type="LINK",
            icon="user-plus",
        )

    return RecentActivityItem(
        **base,
        title="Linked",
        description="Entity linked",
        type="LINK",
        icon="link",
    )

def _format_unlink(base, metadata):
    relationship = metadata.get("relationship")

    if relationship == "CASE_CLIENT":
        return RecentActivityItem(
            **base,
            title="Client removed",
            description=f"Client {metadata.get('child_id')} unlinked",
            type="UNLINK",
            icon="user-minus",
        )

    return RecentActivityItem(
        **base,
        title="Unlinked",
        description="Entity removed",
        type="UNLINK",
        icon="unlink",
    )