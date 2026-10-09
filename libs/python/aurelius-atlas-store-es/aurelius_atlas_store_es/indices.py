"""Index naming.

Every index this system creates is named ``<index_prefix>-<kind>`` (DD-004), so the
prefix alone identifies an installation's data in a shared cluster.
"""

import re

from aurelius_atlas_store_es.settings import ElasticsearchSettings

_KIND_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def index_name(settings: ElasticsearchSettings, kind: str) -> str:
    """Return the full index name for a kind of record.

    Args:
        settings: The store settings that carry the index prefix.
        kind: The record kind, lower-case letters, digits and underscores, starting
            with a letter (for example ``"typedefs"`` or ``"entities"``).

    Returns:
        The index name, ``<index_prefix>-<kind>``.

    Raises:
        ValueError: If ``kind`` does not match the allowed pattern.
    """
    if not _KIND_PATTERN.fullmatch(kind):
        msg = f"invalid index kind {kind!r}: use lower-case letters, digits and underscores"
        raise ValueError(msg)
    return f"{settings.index_prefix}-{kind}"
