"""Lineage as an ArchiMate model for the frontend's model viewer (replaces m4i-lineage-model + m4i-data2model).

``GET /api/aurelius/lineage_model?guid=&depth=3&direction=BOTH`` (the frontend's ``lineage_model``) used to
fetch the Atlas lineage, turn every lineage relation into a row (from/to entity or process) and send the rows with
fixed extraction rules to data2model, which built an ArchiMate model with m4i-analytics and laid it out with
graphviz.  This module produces the same response directly from pyatlas' lineage:

``{"model": "<ar3_model JSON string>", "metadata": [{"id": ..., "data": {...}}, ...]}``

* elements: datasets as ``lineage_dataset``, processes as ``lineage_process`` (named by their display text),
* relationships: one ``lineage_relation`` per lineage relation, id = the Atlas relationship guid,
* one view ``lineage_view`` ("Lineage") laid out left to right in dependency order (layered layout),
* organizations "Other" / "Relations" / "Views" and the extractor metadata (``Type name`` per element),

and 204 (no content) when the entity has no lineage, as before.
"""
from __future__ import annotations

import json
from typing import Dict, List, Tuple

PROCESS_TYPES = {"m4i_generic_process", "m4i_api_operation_process", "m4i_connector_process",
                 "m4i_ingress_controller_process", "m4i_ingress_object_process", "m4i_kubernetes_service_process",
                 "m4i_microservice_process"}
VIEW_ID = "lineage_view"
CREATED_BY = "Model Extractor API"
NODE_W, NODE_H = 120, 55
X0, Y0, DX, DY = 79, 18, 193, 90


def _name(value) -> List[dict]:
    return [{"@xml_lang": "en", "value": "" if value is None else str(value)}]


def _is_process(entity: dict, reg=None) -> bool:
    t = entity.get("typeName")
    if t in PROCESS_TYPES:
        return True
    if reg is not None:
        et = reg.entities.get(t)
        return bool(et and "Process" in et.all_super_types) if hasattr(et, "all_super_types") else False
    return False


def layered_layout(nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Tuple[int, int]]:
    """Left-to-right layers by longest path from the sources (cycle-safe), order within a layer by the average
    position of the predecessors (one barycentre sweep)."""
    succ: Dict[str, List[str]] = {n: [] for n in nodes}
    pred: Dict[str, List[str]] = {n: [] for n in nodes}
    for s, t in edges:
        if s in succ and t in succ and s != t:
            succ[s].append(t)
            pred[t].append(s)
    layer: Dict[str, int] = {}
    state: Dict[str, int] = {}

    def visit(n: str) -> int:              # longest path to n; back edges (cycles) are ignored
        if n in layer:
            return layer[n]
        if state.get(n) == 1:
            return -1
        state[n] = 1
        layer[n] = max((visit(p) + 1 for p in pred[n]), default=0)
        state[n] = 2
        return layer[n]
    for n in nodes:
        visit(n)
    by_layer: Dict[int, List[str]] = {}
    for n in nodes:
        by_layer.setdefault(layer[n], []).append(n)
    pos: Dict[str, Tuple[int, int]] = {}
    index: Dict[str, float] = {}
    for lv in sorted(by_layer):
        members = by_layer[lv]
        if lv > 0:
            members.sort(key=lambda n: (sum(index[p] for p in pred[n] if p in index) /
                                        max(1, sum(1 for p in pred[n] if p in index))) if pred[n] else 0.0)
        for i, n in enumerate(members):
            index[n] = float(i)
            pos[n] = (X0 + lv * DX, Y0 + i * DY)
    return pos


def build(lineage: dict, root_guid: str, reg=None) -> Tuple[int, dict]:
    """(status, body): 204 without lineage relations, otherwise the model and metadata."""
    relations = lineage.get("relations") or []
    guid_map = lineage.get("guidEntityMap") or {}
    if not relations:
        return 204, {}
    elements: Dict[str, dict] = {}          # insertion ordered, last definition wins (drop_duplicates keep=last)
    rels: Dict[str, dict] = {}
    for r in relations:
        f, t = guid_map.get(r.get("fromEntityId")), guid_map.get(r.get("toEntityId"))
        if not f or not t:
            continue
        for e in (f, t):
            kind = "lineage_process" if _is_process(e, reg) else "lineage_dataset"
            elements.pop(e["guid"], None)
            elements[e["guid"]] = {"id": e["guid"], "type": kind, "name": e.get("displayText") or e["guid"],
                                   "typeName": e.get("typeName")}
        rid = r.get("relationshipId") or f"{f['guid']}-{t['guid']}"
        rels[rid] = {"id": rid, "source": f["guid"], "target": t["guid"]}

    pos = layered_layout(list(elements), [(x["source"], x["target"]) for x in rels.values()])
    node_ids = {}
    view_nodes = []
    for i, (g, (x, y)) in enumerate(pos.items()):
        node_ids[g] = f"{VIEW_ID}-{g}--{i}"
        view_nodes.append({"@identifier": node_ids[g], "@x": x, "@y": y, "@w": NODE_W, "@h": NODE_H,
                           "@elementRef": g, "@xsi_type": "ar3_Element"})
    connections = [{"@identifier": f"{VIEW_ID}-{r['id']}--{i}", "@source": node_ids[r["source"]],
                    "@target": node_ids[r["target"]], "@relationshipRef": r["id"], "@xsi_type": "ar3_Relationship"}
                   for i, r in enumerate(rels.values())]
    model = {"ar3_model": {
        "@identifier": "Generated model", "ar3_name": _name("Generated model"),
        "ar3_elements": {"ar3_element": [{"@identifier": e["id"], "@xsi_type": e["type"], "ar3_name": _name(e["name"])}
                                         for e in elements.values()]},
        "ar3_relationships": {"ar3_relationship": [
            {"@identifier": r["id"], "@target": r["target"], "@source": r["source"], "@xsi_type": "lineage_relation",
             "ar3_name": _name("")} for r in rels.values()]},
        "ar3_views": {"ar3_diagrams": {"ar3_view": [{
            "@identifier": VIEW_ID, "@xsi_type": "ar3_Diagram", "ar3_node": view_nodes,
            "ar3_connection": connections, "ar3_name": _name("Lineage")}]}},
        "ar3_organizations": [{"ar3_item": [
            {"ar3_label": _name("Other"), "ar3_item": [{"@identifierRef": g} for g in elements]},
            {"ar3_label": _name("Relations"), "ar3_item": [{"@identifierRef": r} for r in rels]},
            {"ar3_label": _name("Views"), "ar3_item": [{"@identifierRef": VIEW_ID}]}]}],
    }}
    meta = [{"id": e["id"], "data": {"created_by": CREATED_BY, "m4i_id_prefix": "", "m4i_original_id": e["id"],
                                     "Type name": e["typeName"]}} for e in elements.values()]
    meta += [{"id": r, "data": {"created_by": CREATED_BY, "m4i_id_prefix": "", "m4i_original_id": r}} for r in rels]
    meta.append({"id": VIEW_ID, "data": {"created_by": CREATED_BY, "m4i_id_type": "static", "m4i_id_prefix": "",
                                         "m4i_original_id": VIEW_ID, "m4i_path": "Views"}})
    return 200, {"metadata": meta, "model": json.dumps(model)}
