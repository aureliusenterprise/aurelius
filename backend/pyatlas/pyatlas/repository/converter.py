"""Conversions between stored entity documents and the Atlas REST representations."""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional

from ..typesystem.registry import SINGLE, TypeRegistry

HEADER_DEFAULT_ATTRS = ("name", "description", "owner", "createTime", "displayName")

SYSTEM_ATTR_FIELDS = {
    "__guid": ("guid", "str"),
    "__typeName": ("typeName", "str"),
    "__state": ("status", "str"),
    "__entityStatus": ("status", "str"),
    "__timestamp": ("createTime", "lng"),
    "__modificationTimestamp": ("updateTime", "lng"),
    "__createdBy": ("createdBy", "str"),
    "__modifiedBy": ("updatedBy", "str"),
    "__classificationNames": ("classificationNames", "str"),
    "__propagatedClassificationNames": ("propagatedClassificationNames", "str"),
    "__labels": ("labels", "str"),
    "__customAttributes": ("customAttributesKV", "str"),
    "__isIncomplete": ("isIncomplete", "bool"),
    "__meaningNames": ("meaningNames", "str"),
    "__superTypeNames": ("superTypeNames", "str"),
    "__pendingTasks": ("pendingTasks", "str"),
}


def unique_key(type_name: str, attr: str, value: Any) -> str:
    raw = f"{type_name}\x00{attr}\x00{json.dumps(value, sort_keys=True, default=str)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def display_text(reg: TypeRegistry, type_name: str, attrs: Dict[str, Any]) -> Optional[str]:
    dta = reg.display_text_attribute(type_name)
    for k in ([dta] if dta else []) + ["name", "displayName", "qualifiedName"]:
        v = attrs.get(k)
        if v not in (None, ""):
            return str(v)
    return None


def _group_values(reg_attr, v):
    g = reg_attr.index_group
    vals = v if isinstance(v, list) else [v]
    vals = [x for x in vals if x is not None]
    if g == "dbl":
        vals = [float(x) for x in vals]
    elif g == "lng":
        vals = [int(x) for x in vals]
        vals = [x for x in vals if -(2 ** 63) <= x < 2 ** 63]  # biginteger values outside ES long range are not indexed
    elif g == "bool":
        vals = [bool(x) for x in vals]
    else:
        vals = [str(x) for x in vals]
    return g, vals


def _index_attrs(attr_infos, attrs: Dict[str, Any], texts: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for k, v in (attrs or {}).items():
        a = attr_infos.get(k)
        if a is None or a.index_group is None or v is None:
            continue
        g, vals = _group_values(a, v)
        if not vals:
            continue
        idx.setdefault(g, {})[k] = vals if isinstance(v, list) else vals[0]
        if g == "str" and texts is not None:
            texts.extend(vals)
    return idx


def build_index_fields(reg: TypeRegistry, doc: dict) -> dict:
    """(Re)compute all derived/search fields of an entity document in place."""
    t = reg.entities.get(doc["typeName"])
    attrs = doc.get("attributes") or {}
    texts: List[str] = []
    doc["idx"] = _index_attrs(t.attributes if t else {}, attrs, texts)

    bmidx: Dict[str, Dict[str, Any]] = {}
    for bm, bm_attrs in (doc.get("businessAttributes") or {}).items():
        bmt = reg.business_metadata.get(bm)
        if bmt is None:
            continue
        for g, m in _index_attrs(bmt.attributes, bm_attrs, texts).items():
            bmidx.setdefault(g, {})[bm] = m
    doc["bmidx"] = bmidx

    tags = []
    direct_names, prop_names = [], []
    for c in doc.get("classifications") or []:
        ct = reg.classifications.get(c["typeName"])
        tags.append({"typeName": c["typeName"], "propagated": False, "source": doc["guid"],
                     "idx": _index_attrs(ct.attributes if ct else {}, c.get("attributes") or {})})
        direct_names.append(c["typeName"])
    for c in doc.get("propagatedClassifications") or []:
        ct = reg.classifications.get(c["typeName"])
        tags.append({"typeName": c["typeName"], "propagated": True, "source": c.get("entityGuid"),
                     "idx": _index_attrs(ct.attributes if ct else {}, c.get("attributes") or {})})
        prop_names.append(c["typeName"])
    doc["tags"] = tags
    doc["classificationNames"] = sorted(set(direct_names))
    doc["propagatedClassificationNames"] = sorted(set(prop_names))
    doc["allClassificationNames"] = sorted(set(direct_names) | set(prop_names))
    doc["superTypeNames"] = sorted(t.all_super_types) if t else []
    doc["displayText"] = display_text(reg, doc["typeName"], attrs)
    doc["customAttributesKV"] = [f"{k}={v}" for k, v in (doc.get("customAttributes") or {}).items()]
    parts = [doc["typeName"]] + ([doc["displayText"]] if doc["displayText"] else []) + texts \
        + doc["allClassificationNames"] + list(doc.get("labels") or []) + list(doc.get("meaningNames") or [])
    doc["fulltext"] = " ".join(str(p) for p in parts)
    return doc


def build_relationship_index_fields(reg: TypeRegistry, rel: dict) -> dict:
    rt = reg.relationships.get(rel.get("typeName"))
    rel["idx"] = _index_attrs(rt.attribute_defs if rt else {}, rel.get("attributes") or {})
    return rel


def strip_internal(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if not k.startswith("_")}


# --------------------------------------------------------------------- API shapes
def classification_to_api(c: dict, entity_guid: str, entity_status: str) -> dict:
    out = {
        "typeName": c["typeName"],
        "attributes": copy.deepcopy(c.get("attributes") or {}),
        "entityGuid": c.get("entityGuid") or entity_guid,
        "entityStatus": c.get("entityStatus") or entity_status,
        "propagate": c.get("propagate", True),
        "removePropagationsOnEntityDelete": c.get("removePropagationsOnEntityDelete", False),
    }
    if c.get("validityPeriods"):
        out["validityPeriods"] = c["validityPeriods"]
    return out


def all_classifications_api(doc: dict) -> List[dict]:
    st = doc.get("status", "ACTIVE")
    out = [classification_to_api(c, doc["guid"], st) for c in doc.get("classifications") or []]
    out += [classification_to_api(c, c.get("entityGuid"), c.get("entityStatus", "ACTIVE"))
            for c in doc.get("propagatedClassifications") or []]
    return out


def unique_attributes_of(reg: TypeRegistry, doc: dict) -> Dict[str, Any]:
    t = reg.entities.get(doc["typeName"])
    attrs = doc.get("attributes") or {}
    if t is None:
        return {}
    return {u: attrs.get(u) for u in t.unique_attributes if attrs.get(u) is not None}


def object_id(reg: TypeRegistry, doc: dict) -> dict:
    return {"guid": doc["guid"], "typeName": doc["typeName"], "uniqueAttributes": unique_attributes_of(reg, doc)}


def entity_header(reg: TypeRegistry, doc: dict, extra_attrs: Iterable[str] = (),
                  rel_values: Optional[Dict[str, Any]] = None) -> dict:
    attrs_src = doc.get("attributes") or {}
    attrs = unique_attributes_of(reg, doc)
    for k in HEADER_DEFAULT_ATTRS:
        if attrs_src.get(k) is not None:
            attrs[k] = attrs_src[k]
    for k in extra_attrs or ():
        if k in attrs_src:
            attrs[k] = attrs_src[k]
        elif rel_values and k in rel_values:
            attrs[k] = rel_values[k]
        elif k.startswith("__"):
            f = SYSTEM_ATTR_FIELDS.get(k)
            if f:
                attrs[k] = doc.get(f[0])
    classifications = all_classifications_api(doc)
    return {
        "typeName": doc["typeName"],
        "attributes": attrs,
        "guid": doc["guid"],
        "status": doc.get("status", "ACTIVE"),
        "displayText": doc.get("displayText") or display_text(reg, doc["typeName"], attrs_src),
        "classificationNames": doc.get("allClassificationNames") or sorted({c["typeName"] for c in classifications}),
        "classifications": classifications,
        "meaningNames": list(doc.get("meaningNames") or []),
        "meanings": [dict(m) for m in doc.get("meanings") or []],
        "isIncomplete": bool(doc.get("isIncomplete", False)),
        "labels": list(doc.get("labels") or []),
    }


def related_object_id(reg: TypeRegistry, other: dict, rel: dict) -> dict:
    rel_attrs = rel.get("attributes") or {}
    out = {
        "guid": other["guid"],
        "typeName": other["typeName"],
        "entityStatus": other.get("status", "ACTIVE"),
        "displayText": other.get("displayText"),
        "relationshipType": rel["typeName"],
        "relationshipGuid": rel["guid"],
        "relationshipStatus": rel.get("status", "ACTIVE"),
        "relationshipAttributes": {"typeName": rel["typeName"], "attributes": copy.deepcopy(rel_attrs)},
    }
    qn = (other.get("attributes") or {}).get("qualifiedName")
    if qn is not None:
        out["qualifiedName"] = qn
        out["uniqueAttributes"] = {"qualifiedName": qn}
    return out


def entity_to_api(reg: TypeRegistry, doc: dict, rels: Optional[List[dict]] = None,
                  others: Optional[Dict[str, dict]] = None, include_relationships: bool = True) -> dict:
    t = reg.entities.get(doc["typeName"])
    stored = doc.get("attributes") or {}
    attrs: Dict[str, Any] = {}
    if t is not None:
        for name, a in t.attributes.items():
            if a.is_object_ref:
                continue
            attrs[name] = copy.deepcopy(stored.get(name))
    else:
        attrs = copy.deepcopy(stored)
    entity: Dict[str, Any] = {
        "typeName": doc["typeName"],
        "attributes": attrs,
        "guid": doc["guid"],
        "isIncomplete": bool(doc.get("isIncomplete", False)),
        "provenanceType": doc.get("provenanceType", 0),
        "status": doc.get("status", "ACTIVE"),
        "createdBy": doc.get("createdBy"),
        "updatedBy": doc.get("updatedBy"),
        "createTime": doc.get("createTime"),
        "updateTime": doc.get("updateTime"),
        "version": doc.get("version", 0),
        "classifications": all_classifications_api(doc),
        "labels": list(doc.get("labels") or []),
    }
    if doc.get("meanings"):
        entity["meanings"] = [dict(m) for m in doc["meanings"]]
    if doc.get("homeId"):
        entity["homeId"] = doc["homeId"]
    if doc.get("isProxy"):
        entity["isProxy"] = True
    if doc.get("customAttributes"):
        entity["customAttributes"] = copy.deepcopy(doc["customAttributes"])
    if doc.get("businessAttributes"):
        entity["businessAttributes"] = copy.deepcopy(doc["businessAttributes"])
    if doc.get("pendingTasks"):
        entity["pendingTasks"] = list(doc["pendingTasks"])
    if not include_relationships or t is None:
        return entity

    rel_attrs: Dict[str, Any] = {}
    legacy_attrs: Dict[str, Any] = {}
    # initialise every relationship attribute as Atlas does
    for name, ends in t.relationship_attributes.items():
        single = all(e.cardinality == SINGLE for e in ends)
        synthetic_only = all(e.rel.synthetic for e in ends)
        target = legacy_attrs if synthetic_only else rel_attrs
        target[name] = None if single else []
    # reference attributes (attributeDefs of an entity type) whose values live in relationships of the same name:
    # Atlas returns them in "attributes" too, as plain object ids (EntityGraphRetriever.mapVertexToObjectId),
    # including references to deleted entities.  Only for attributes the type declares itself: for attributes
    # inherited from a supertype Atlas looks for an edge label that relationships do not use and returns them
    # empty (e.g. m4i_referenceable.source on every m4i type, see Aurelius' sample export).
    ref_attrs: Dict[str, Any] = {}
    for name, ai in (t.attributes or {}).items():
        if ai.is_object_ref and not ai.is_soft_ref and ai.declaring_type == t.name \
                and name in t.relationship_attributes \
                and not all(e.rel.synthetic for e in t.relationship_attributes[name]):
            ref_attrs[name] = [] if ai.kind == "array" else None
    for r in _visible_rels(doc, rels or [], others or {}):
        rt = reg.relationships.get(r["typeName"])
        if rt is None:
            continue
        for end_no in (1, 2):
            if r[f"end{end_no}Guid"] != doc["guid"]:
                continue
            end = rt.end(end_no)
            if not end.name:
                continue
            other_guid = r[f"end{2 if end_no == 1 else 1}Guid"]
            other = (others or {}).get(other_guid)
            if other is None:
                continue
            if rt.synthetic:
                val = object_id(reg, other)
                target = legacy_attrs
            else:
                val = related_object_id(reg, other, r)
                target = rel_attrs
            if end.cardinality == SINGLE:
                if target.get(end.name) is None or r.get("status") == "ACTIVE":
                    target[end.name] = val
            else:
                cur = target.get(end.name)
                if not isinstance(cur, list):
                    cur = []
                    target[end.name] = cur
                cur.append(val)
            if end.name in ref_attrs and not rt.synthetic:
                oid = object_id(reg, other)
                if isinstance(ref_attrs[end.name], list):
                    ref_attrs[end.name].append(oid)
                elif ref_attrs[end.name] is None or r.get("status") == "ACTIVE":
                    ref_attrs[end.name] = oid
            # legacy (isLegacyAttribute) relationship attributes are also exposed in "attributes"
            if end.is_legacy and not rt.synthetic and end.name in (t.attributes or {}):
                legacy_attrs[end.name] = copy.deepcopy(target[end.name])
    for k, v in ref_attrs.items():
        attrs[k] = v
    for k, v in legacy_attrs.items():
        attrs[k] = v
    entity["relationshipAttributes"] = rel_attrs
    return entity


def _visible_rels(doc: dict, rels: List[dict], others: Dict[str, dict]) -> List[dict]:
    """Active relationships, plus relationships deleted together with an entity (soft delete)."""
    out = []
    me_deleted = doc.get("status") == "DELETED"
    for r in rels:
        if r.get("status") == "ACTIVE":
            out.append(r)
            continue
        if not r.get("deletedByEntity"):
            continue
        other_guid = r["end2Guid"] if r["end1Guid"] == doc["guid"] else r["end1Guid"]
        other = others.get(other_guid)
        if me_deleted or (other is not None and other.get("status") == "DELETED"):
            out.append(r)
    out.sort(key=lambda r: (r.get("endIndex") if r.get("endIndex") is not None else 1 << 30, r.get("createTime") or 0))
    return out


def relationship_to_api(reg: TypeRegistry, r: dict, end1: Optional[dict], end2: Optional[dict]) -> dict:
    def end(d, guid, tname):
        if d is None:
            return {"guid": guid, "typeName": tname}
        return object_id(reg, d)
    out = {
        "typeName": r["typeName"],
        "attributes": copy.deepcopy(r.get("attributes") or {}),
        "guid": r["guid"],
        "provenanceType": r.get("provenanceType", 0),
        "end1": end(end1, r["end1Guid"], r.get("end1Type")),
        "end2": end(end2, r["end2Guid"], r.get("end2Type")),
        "label": r.get("label"),
        "propagateTags": r.get("propagateTags", "NONE"),
        "status": r.get("status", "ACTIVE"),
        "createdBy": r.get("createdBy"),
        "updatedBy": r.get("updatedBy"),
        "createTime": r.get("createTime"),
        "updateTime": r.get("updateTime"),
        "version": r.get("version", 0),
        "blockedPropagatedClassifications": copy.deepcopy(r.get("blockedPropagatedClassifications") or []),
        "propagatedClassifications": [],
    }
    if r.get("homeId"):
        out["homeId"] = r["homeId"]
    # classifications currently flowing across this edge
    pt = r.get("propagateTags", "NONE")
    flows = []
    if pt in ("ONE_TO_TWO", "BOTH") and end1 is not None and end2 is not None:
        flows.append((end1, end2))
    if pt in ("TWO_TO_ONE", "BOTH") and end1 is not None and end2 is not None:
        flows.append((end2, end1))
    seen = set()
    blocked = {(b.get("typeName"), b.get("entityGuid")) for b in out["blockedPropagatedClassifications"]}
    for src, dst in flows:
        src_tags = {(c["typeName"], src["guid"]) for c in src.get("classifications") or []}
        src_tags |= {(c["typeName"], c.get("entityGuid")) for c in src.get("propagatedClassifications") or []}
        for c in dst.get("propagatedClassifications") or []:
            key = (c["typeName"], c.get("entityGuid"))
            if key in src_tags and key not in seen and key not in blocked:
                seen.add(key)
                out["propagatedClassifications"].append(classification_to_api(c, c.get("entityGuid"), "ACTIVE"))
    return out
