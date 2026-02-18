DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def normalize_pagination(
    limit: int | None = None, offset: int | None = None
) -> tuple[int, int]:
    l = DEFAULT_LIMIT if limit is None else min(limit or DEFAULT_LIMIT, MAX_LIMIT)
    o = 0 if offset is None else max(0, offset)
    return l, o
