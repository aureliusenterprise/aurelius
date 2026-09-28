"""Data quality results (replaces the Kafka quality topics and m4i-atlas-post-install ``propagate_quality.py``).

Data quality rules (``m4i_data_quality`` entities: an expression on a field) are run against the data by quality
tooling outside pyatlas.  The tooling posts the scores to ``POST /api/aurelius/quality/results``:

    {"results": [{"quality": "<guid or qualifiedName of the m4i_data_quality entity>", "dqscore": 0.93,
                  "businessRuleId": 43, "dataDomainName": "Finance"}]}

pyatlas stores one document per rule in the ``atlas-dev-quality`` engine (id = the rule's qualified name, as
before) and fills everything else from the metadata: expression, description, dimension and the field it checks.
The data domain is the one the tooling ran for (``dataDomainName``), else the domain of the field's data
attribute.  These fields follow later changes of the rule entity; results of deleted rules
disappear.  The scores roll up field -> data attribute -> breadcrumb ancestors in the search documents
(:func:`.search_docs.apply_quality`).
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

QUALITY_TYPE = "m4i_data_quality"


def _first_ref(value) -> Optional[dict]:
    if isinstance(value, list):
        return value[0] if value else None
    return value if isinstance(value, dict) else None


def rule_metadata(rule: Mapping[str, Any], entities: Mapping[str, Mapping[str, Any]]) -> dict:
    """The document fields that come from the ``m4i_data_quality`` entity and its field."""
    a = rule.get("attributes") or {}
    field_ref = _first_ref((rule.get("relationshipAttributes") or {}).get("fields")) or _first_ref(a.get("fields"))
    field = entities.get(field_ref.get("guid")) if field_ref else None
    field_qn = ((field or {}).get("attributes") or {}).get("qualifiedName") \
        or ((field_ref or {}).get("uniqueAttributes") or {}).get("qualifiedName")
    return {
        "qualityguid": rule["guid"], "guid": rule["guid"], "expression": a.get("expression"),
        "qualityqualifiedname": a.get("qualifiedName"), "dataqualityruledescription": a.get("ruleDescription"),
        "dataqualityruledimension": a.get("qualityDimension"),
        "fieldguid": field_ref.get("guid") if field_ref else None, "fieldqualifiedname": field_qn,
    }


def new_document(rule: Mapping[str, Any], entities: Mapping[str, Mapping[str, Any]], dqscore: float,
                 business_rule_id: Any = None, data_domain_name: Optional[str] = None) -> dict:
    a = rule.get("attributes") or {}
    rid = business_rule_id if business_rule_id is not None else a.get("id")
    doc = {"id": a.get("qualifiedName") or rule["guid"], "dqscore": float(dqscore),
           "businessruleid": float(rid) if isinstance(rid, (int, float)) else rid,
           "name": f"Rule {int(rid) if isinstance(rid, float) and rid.is_integer() else rid}"
           if rid is not None else a.get("name"),
           "datadomainname": data_domain_name or None}
    doc.update(rule_metadata(rule, entities))
    return doc


def refresh(documents: Iterable[dict], entities: Mapping[str, Mapping[str, Any]]) -> List[dict]:
    """Stored result documents with their metadata re-read from the rule entities; results whose rule entity is
    gone (or no longer active) are dropped."""
    out = []
    for d in documents:
        rule = entities.get(d.get("qualityguid") or d.get("guid"))
        if rule is None or rule.get("typeName") != QUALITY_TYPE or rule.get("status", "ACTIVE") != "ACTIVE":
            continue
        d = dict(d)
        d.update(rule_metadata(rule, entities))
        out.append(d)
    return out


def fill_domain_names(documents: List[dict], search_docs: Mapping[str, dict]) -> None:
    """``datadomainname`` where the tooling did not name it: the data domain of the field's data attribute."""
    for d in documents:
        if d.get("datadomainname"):
            continue
        name = None
        field = search_docs.get(d.get("fieldguid") or "")
        for attr_guid in (field or {}).get("deriveddataattributeguid") or []:
            attr = search_docs.get(attr_guid) or {}
            for n, t in zip(attr.get("breadcrumbname") or [], attr.get("breadcrumbtype") or []):
                if t == "m4i_data_domain":
                    name = n
                    break
            if name:
                break
        d["datadomainname"] = name


def resolve(refs: Iterable[str], entities: Mapping[str, Mapping[str, Any]]) -> Tuple[Dict[str, dict], List[str]]:
    """Rule entities by the given guids or qualified names; the second value lists the unknown references."""
    by_qn = {(e.get("attributes") or {}).get("qualifiedName"): e for e in entities.values()
             if e.get("typeName") == QUALITY_TYPE and e.get("status", "ACTIVE") == "ACTIVE"}
    found, unknown = {}, []
    for r in refs:
        e = entities.get(r)
        if e is None or e.get("typeName") != QUALITY_TYPE or e.get("status", "ACTIVE") != "ACTIVE":
            e = by_qn.get(r)
        if e is None:
            unknown.append(r)
        else:
            found[r] = e
    return found, unknown
