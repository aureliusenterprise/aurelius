"""Overview of a dataset for the frontend (``/api/aurelius/datasets/{guid}/...``): its lineage as a graph and its
fields as a table with the data dictionary behind them.

A dataset only knows its fields; the attribute behind a field (``m4i_data_attribute_field_assignment``), the
attribute's description and the data entities it belongs to are one and two relationships further.  The frontend
would need an entity request per field and per attribute; these endpoints walk the graph on the server in a few
bulk reads instead.  All reads go through the entity store, so the usual entity-read authorization applies.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ..errors import AtlasBaseException, AtlasErrorCode

DATASET_TYPE = "m4i_dataset"
_BATCH = 200
MAX_DEPTH = 10


def _active(refs: Optional[Iterable[dict]]) -> List[dict]:
    """The related entities of a relationship attribute that still exist (not deleted, relationship not deleted)."""
    return [r for r in refs or [] if r and r.get("guid")
            and r.get("relationshipStatus", "ACTIVE") != "DELETED" and r.get("entityStatus", "ACTIVE") != "DELETED"]


def _ref(r: dict) -> dict:
    return {"guid": r["guid"], "typeName": r.get("typeName"), "name": r.get("displayText") or r["guid"]}


async def _entities(services, guids: List[str]) -> Dict[str, dict]:
    """The entities (API form, with relationship attributes) by guid, read in batches."""
    out: Dict[str, dict] = {}
    unique = list(dict.fromkeys(guids))
    for i in range(0, len(unique), _BATCH):
        res = await services.entities.get_by_guids(unique[i:i + _BATCH])
        for e in res.get("entities") or []:
            out[e["guid"]] = e
    return out


def _classifications(entity: dict) -> List[dict]:
    """The classifications of an entity, own and inherited (propagated from another entity)."""
    seen, out = set(), []
    for c in entity.get("classifications") or []:
        key = (c.get("typeName"), c.get("entityGuid"))
        if key in seen:
            continue
        seen.add(key)
        source = c.get("entityGuid")
        out.append({"typeName": c.get("typeName"), "inherited": bool(source) and source != entity["guid"],
                    "source": source})
    return out


async def fields(services, guid: str) -> dict:
    """The dataset with one row per field: the field, the attributes it is assigned to with their description and
    data entities, and the field's classifications."""
    base = (await services.entities.get_by_guid(guid))["entity"]
    if base.get("typeName") != DATASET_TYPE:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"{guid} is not a dataset ({DATASET_TYPE})")
    ra = base.get("relationshipAttributes") or {}
    field_refs = _active(ra.get("fields"))
    field_docs = await _entities(services, [r["guid"] for r in field_refs])
    attr_guids = [r["guid"] for f in field_docs.values()
                  for r in _active((f.get("relationshipAttributes") or {}).get("attributes"))]
    attr_docs = await _entities(services, attr_guids)

    def attribute(a: dict) -> dict:
        aa, ar = a.get("attributes") or {}, a.get("relationshipAttributes") or {}
        return {"guid": a["guid"], "name": aa.get("name") or aa.get("qualifiedName"),
                "qualifiedName": aa.get("qualifiedName"), "definition": aa.get("definition"),
                "dataEntities": sorted((_ref(r) for r in _active(ar.get("dataEntity"))),
                                       key=lambda r: r["name"].casefold()),
                "classifications": _classifications(a)}

    rows = []
    for ref in field_refs:
        f = field_docs.get(ref["guid"])
        if f is None or f.get("status") == "DELETED":
            continue
        fa, fr = f.get("attributes") or {}, f.get("relationshipAttributes") or {}
        attrs = [attribute(attr_docs[r["guid"]]) for r in _active(fr.get("attributes")) if r["guid"] in attr_docs]
        rows.append({"guid": f["guid"], "name": fa.get("name") or fa.get("qualifiedName"),
                     "qualifiedName": fa.get("qualifiedName"), "fieldType": fa.get("fieldType"),
                     "definition": fa.get("definition"),
                     "attributes": sorted(attrs, key=lambda x: ((x["name"] or "").casefold(), x["guid"])),
                     "classifications": _classifications(f)})
    rows.sort(key=lambda r: ((r["name"] or "").casefold(), r["guid"]))

    entities = {e["guid"] for r in rows for a in r["attributes"] for e in a["dataEntities"]}
    attributes = {a["guid"] for r in rows for a in r["attributes"]}
    ba = base.get("attributes") or {}
    return {
        "dataset": {"guid": base["guid"], "typeName": base["typeName"], "name": ba.get("name") or ba.get("qualifiedName"),
                    "qualifiedName": ba.get("qualifiedName"), "definition": ba.get("definition"),
                    "collections": [_ref(r) for r in _active(ra.get("collections"))]},
        "fields": rows,
        "summary": {"fields": len(rows), "withAttribute": sum(1 for r in rows if r["attributes"]),
                    "withoutAttribute": sum(1 for r in rows if not r["attributes"]),
                    "attributes": len(attributes), "dataEntities": len(entities)},
    }


async def lineage(services, guid: str, depth: int = 3) -> dict:
    """The lineage of ``guid`` in both directions as nodes (datasets and processes, datasets with their number of
    fields) and edges in the direction of the data flow."""
    depth = max(1, min(int(depth), MAX_DEPTH))
    lin = await services.lineage.lineage(guid, "BOTH", depth)
    reg = services.typedefs.registry
    headers: Dict[str, Any] = dict(lin.get("guidEntityMap") or {})
    if guid not in headers:                       # no lineage: the entity on its own
        e = (await services.entities.get_by_guid(guid, min_ext_info=True))["entity"]
        headers[guid] = {"guid": guid, "typeName": e.get("typeName"), "attributes": e.get("attributes") or {},
                         "status": e.get("status")}

    def kind(type_name: str) -> str:
        t = reg.entities.get(type_name)
        return "process" if t is not None and t.isa("Process") else "dataset"

    nodes = []
    for g, h in headers.items():
        a = h.get("attributes") or {}
        nodes.append({"guid": g, "typeName": h.get("typeName"), "kind": kind(h.get("typeName")),
                      "name": a.get("name") or h.get("displayText") or a.get("qualifiedName") or g,
                      "status": h.get("status", "ACTIVE"), "fieldCount": None})
    datasets = [n["guid"] for n in nodes if n["typeName"] == DATASET_TYPE]
    docs = await _entities(services, datasets)
    for n in nodes:
        d = docs.get(n["guid"])
        if d is not None:
            n["fieldCount"] = len(_active((d.get("relationshipAttributes") or {}).get("fields")))
    edges = [{"from": r["fromEntityId"], "to": r["toEntityId"]} for r in lin.get("relations") or []
             if r.get("fromEntityId") in headers and r.get("toEntityId") in headers]
    return {"baseEntityGuid": guid, "depth": depth, "nodes": nodes, "edges": edges}


__all__ = ["fields", "lineage"]
