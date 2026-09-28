"""GUID-independent comparison: replaces entity guids by ``qn:<qualifiedName>``.

Two servers that received the same changes (``parity mutate``) assign different guids, so documents are
matched and compared by qualified name instead.  ``guid_map`` maps guid -> qualifiedName; any string value
that is a known guid (also inside ``a--b`` composite ids) is rewritten.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable

_GUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def guid_map_from_documents(docs: Iterable[dict]) -> Dict[str, str]:
    """guid -> qualified name from search documents (``guid`` + ``referenceablequalifiedname`` / ``qualifiedname``)."""
    out = {}
    for d in docs:
        g = d.get("guid")
        qn = d.get("referenceablequalifiedname") or d.get("qualityqualifiedname") or d.get("qualifiedname")
        if g and qn:
            out[str(g)] = str(qn)
    return out


def guid_map_from_entities(entities: Iterable[dict]) -> Dict[str, str]:
    out = {}
    for e in entities:
        qn = (e.get("attributes") or {}).get("qualifiedName")
        if e.get("guid") and qn:
            out[e["guid"]] = f"{e.get('typeName')}:{qn}"
    return out


def canonicalize(value: Any, guid_map: Dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {k: canonicalize(v, guid_map) for k, v in value.items()}
    if isinstance(value, list):
        return [canonicalize(v, guid_map) for v in value]
    if isinstance(value, str) and _GUID.search(value):
        return _GUID.sub(lambda m: f"qn:{guid_map[m.group(0)]}" if m.group(0) in guid_map else m.group(0), value)
    return value
