import re


def sanitize_tsquery(search: str | None) -> str | None:
    """
    Sanitize search query for PostgreSQL full-text search.

    Escapes special characters that could be interpreted as tsquery operators:
    - &: AND operator
    - |: OR operator
    - !: NOT operator
    - (: grouping
    - ): grouping
    - " : phrase matching

    Also removes control characters (ASCII 0x00-0x1F) to prevent potential issues.

    Args:
        search: The raw search query string.

    Returns:
        Sanitized search query or None if input is empty/whitespace only.
    """
    if not search:
        return None

    # Escape special tsquery operators by prefixing with backslash
    # Order matters - escape " first to avoid double-escaping
    sanitized = re.sub(r'(["&|!:()])', r"\\\1", search)

    # Remove null bytes and control characters (ASCII 0x00-0x1F)
    sanitized = re.sub(r"[\x00-\x1f]", "", sanitized)

    return sanitized if sanitized.strip() else None
