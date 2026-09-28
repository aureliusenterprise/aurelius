"""Aurelius search documents (the ``atlas-dev`` App Search engine), computed from the metadata graph.

Replaces the Flink job ``m4i-synchronize-app-search`` (and ``m4i-publish-state`` / ``m4i-get-entity``), which
patched these documents message by message from Kafka.  Here a document is a pure function of the graph:

* identity: ``guid``/``id``, ``name`` (or the qualified name), ``referenceablequalifiedname``, ``typename``,
  ``supertypenames``, ``definition``, ``email`` (people), ``sourcetype`` (Business / Technical);
* ``derived<type>`` / ``derived<type>guid``: the directly related entities per Aurelius type
  (``RELATIONSHIP_MAP``), in both directions, except data quality rules and sources (``RELATIONSHIP_BLACKLIST``);
* data entities and datasets are also linked when a field of the dataset realises an attribute of the entity
  (``m4i-atlas-post-install/scripts/connect_datasets_with_entities.py``);
* ``breadcrumb{guid,name,type}`` + ``parentguid``: the chain of first parents up to the root
  (``PARENTS`` = ``get_parents()`` of the m4i-atlas-core entity classes);
* ``dqscore*`` / ``qualityguid_*``: data quality results (``atlas-dev-quality`` documents) of the fields, added to
  their data attributes and to every breadcrumb ancestor, per dimension and overall (the algorithm of
  ``m4i-atlas-post-install/scripts/propagate_quality.py``);
* ``classificationstext``: the entity's classifications.

``build_documents`` is deterministic and has no I/O, so the whole index can be rebuilt at any time and single
documents can be recomputed from their neighbourhood (:func:`affected_guids`).
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

RELATIONSHIP_MAP = {
    "m4i_data_domain": "deriveddatadomain",
    "m4i_data_entity": "deriveddataentity",
    "m4i_data_attribute": "deriveddataattribute",
    "m4i_field": "derivedfield",
    "m4i_dataset": "deriveddataset",
    "m4i_collection": "derivedcollection",
    "m4i_system": "derivedsystem",
    "m4i_person": "derivedperson",
    "m4i_generic_process": "derivedprocess",
}
RELATIONSHIP_BLACKLIST = {"m4i_data_quality", "m4i_gov_data_quality", "m4i_source"}
TECHNICAL_TYPES = {"m4i_system", "m4i_collection", "m4i_dataset", "m4i_field"}
BUSINESS_TYPES = {"m4i_data_domain", "m4i_data_entity", "m4i_data_attribute"}
# the relationship attributes that lead to the parent, in order of preference (m4i-atlas-core get_parents())
PARENTS = {
    "m4i_data_entity": ["parentEntity", "dataDomain"],
    "m4i_data_attribute": ["dataEntity"],
    "m4i_dataset": ["parentDataset", "collections"],
    "m4i_field": ["parentField", "datasets"],
    "m4i_collection": ["systems"],
    "m4i_system": ["parentSystem"],
}
# types that get a search document: every Aurelius type except sources (as the Flink job)
DOCUMENT_TYPES = set(RELATIONSHIP_MAP) | {"m4i_data_quality", "m4i_gov_data_quality"}
DIMENSIONS = ("accuracy", "timeliness", "validity", "completeness", "uniqueness")

LIST_FIELDS = [f for base in RELATIONSHIP_MAP.values() for f in (base, f"{base}guid")] + [
    "breadcrumbname", "breadcrumbguid", "breadcrumbtype", "classificationstext", "supertypenames",
    "deriveddatasetnames", "derivedentityguids", "deriveddatasetguids", "derivedentitynames",
] + [f"qualityguid_{d}" for d in DIMENSIONS]
NONE_FIELDS = ["parentguid", "entityname", "definition", "email", "deriveddataownerguid", "deriveddomainleadguid",
               "deriveddatastewardguid"]
SCORE_FIELDS = [f"{p}_{d}" for d in (*DIMENSIONS, "overall") for p in ("dqscore", "dqscoresum", "dqscorecnt")] + [
    "businessruleid"]


def is_document_type(type_name: Optional[str]) -> bool:
    return type_name in DOCUMENT_TYPES


def sourcetype(type_name: str) -> str:
    if type_name in TECHNICAL_TYPES:
        return "Technical"
    if type_name in BUSINESS_TYPES:
        return "Business"
    return ""


def _refs(value) -> List[dict]:
    """Active related object ids of a relationship attribute value (single or list)."""
    items = value if isinstance(value, list) else [value] if value else []
    return [r for r in items if isinstance(r, dict) and r.get("guid")
            and r.get("relationshipStatus", "ACTIVE") == "ACTIVE" and r.get("entityStatus", "ACTIVE") == "ACTIVE"]


def _name(e: dict) -> str:
    a = e.get("attributes") or {}
    return a.get("name") or a.get("qualifiedName") or e.get("guid")


def empty_document(e: dict) -> Dict[str, Any]:
    a = e.get("attributes") or {}
    t = e.get("typeName")
    doc: Dict[str, Any] = {k: [] for k in LIST_FIELDS}
    doc.update({k: None for k in NONE_FIELDS})
    doc.update({k: 0.0 for k in SCORE_FIELDS})
    doc.update({"id": e["guid"], "guid": e["guid"], "name": _name(e),
                "referenceablequalifiedname": a.get("qualifiedName") or e["guid"], "typename": t,
                "supertypenames": [t], "definition": a.get("definition"), "sourcetype": sourcetype(t)})
    if t == "m4i_person":
        doc["email"] = a.get("email")
    doc["classificationstext"] = sorted({c.get("typeName") for c in e.get("classifications") or []
                                         if c.get("typeName")})
    return doc


def build_documents(entities: Dict[str, dict], quality_documents: Iterable[dict] = ()) -> Dict[str, dict]:
    """Search documents for all document-type entities of ``entities`` (guid -> Atlas entity JSON with
    ``relationshipAttributes``).  Related entities missing from ``entities`` are ignored."""
    docs = {g: empty_document(e) for g, e in entities.items()
            if is_document_type(e.get("typeName")) and e.get("status", "ACTIVE") == "ACTIVE"}

    # derived relationships (both directions come from each side's relationship attributes)
    for g, doc in docs.items():
        if doc["typename"] not in RELATIONSHIP_MAP:
            continue
        for value in (entities[g].get("relationshipAttributes") or {}).values():
            for ref in _refs(value):
                other = docs.get(ref["guid"])
                if other is None or other["typename"] not in RELATIONSHIP_MAP:
                    continue
                field = RELATIONSHIP_MAP[other["typename"]]
                if other["guid"] not in doc[f"{field}guid"]:
                    doc[f"{field}guid"].append(other["guid"])
                    doc[field].append(other["name"])

    # data entities <-> datasets through field -> data attribute -> data entity
    # (m4i-atlas-post-install/scripts/connect_datasets_with_entities.py)
    for doc in docs.values():
        if doc["typename"] != "m4i_field":
            continue
        for attr_guid in doc["deriveddataattributeguid"]:
            for entity_guid in docs[attr_guid]["deriveddataentityguid"]:
                for dataset_guid in doc["deriveddatasetguid"]:
                    ent, ds = docs[entity_guid], docs[dataset_guid]
                    if dataset_guid not in ent["deriveddatasetguid"]:
                        ent["deriveddatasetguid"].append(dataset_guid)
                        ent["deriveddataset"].append(ds["name"])
                    if entity_guid not in ds["deriveddataentityguid"]:
                        ds["deriveddataentityguid"].append(entity_guid)
                        ds["deriveddataentity"].append(ent["name"])

    # breadcrumbs: chain of first parents (cycle-safe)
    parent_of: Dict[str, Optional[str]] = {}
    for g, doc in docs.items():
        parent_of[g] = None
        rels = entities[g].get("relationshipAttributes") or {}
        for attr in PARENTS.get(doc["typename"], ()):
            refs = [r for r in _refs(rels.get(attr)) if r["guid"] in docs]
            if refs:
                # the most recently linked parent wins (the Flink job overwrote the parent on every new link)
                parent_of[g] = refs[-1]["guid"]
                break
    for g, doc in docs.items():
        chain: List[str] = []
        p = parent_of.get(g)
        while p is not None and p not in chain and p != g:
            chain.append(p)
            p = parent_of.get(p)
        chain.reverse()
        doc["breadcrumbguid"] = chain
        doc["breadcrumbname"] = [docs[c]["name"] for c in chain]
        doc["breadcrumbtype"] = [docs[c]["typename"] for c in chain]
        doc["parentguid"] = chain[-1] if chain else None

    apply_quality(docs, quality_documents)
    return docs


def apply_quality(docs: Dict[str, dict], quality_documents: Iterable[dict]) -> None:
    """Data quality scores: field results, summed into the field's data attributes, then every field and
    attribute adds its sums to its breadcrumb ancestors; score = sum / count; overall over all dimensions."""
    for q in quality_documents:
        field = docs.get(q.get("fieldguid"))
        dim = str(q.get("dataqualityruledimension") or "").lower()
        if field is None or dim not in DIMENSIONS:
            continue
        field[f"dqscoresum_{dim}"] += float(q.get("dqscore") or 0.0)
        field[f"dqscorecnt_{dim}"] += 1
        field[f"dqscore_{dim}"] = field[f"dqscoresum_{dim}"] / field[f"dqscorecnt_{dim}"]
        field[f"qualityguid_{dim}"].append(q.get("qualityguid") or q.get("guid"))
    for doc in docs.values():
        if doc["typename"] == "m4i_field":
            for attr_guid in doc["deriveddataattributeguid"]:
                if attr_guid in docs:
                    _add_scores(doc, docs[attr_guid])
    for doc in docs.values():
        if doc["typename"] in ("m4i_data_attribute", "m4i_field"):
            for up in doc["breadcrumbguid"]:
                if up in docs:
                    _add_scores(doc, docs[up])
    for doc in docs.values():
        for d in DIMENSIONS:
            doc["dqscoresum_overall"] += doc[f"dqscoresum_{d}"]
            doc["dqscorecnt_overall"] += doc[f"dqscorecnt_{d}"]
        if doc["dqscorecnt_overall"]:
            doc["dqscore_overall"] = doc["dqscoresum_overall"] / doc["dqscorecnt_overall"]


def _add_scores(down: dict, up: dict) -> None:
    for d in DIMENSIONS:
        up[f"dqscoresum_{d}"] += down[f"dqscoresum_{d}"]
        up[f"dqscorecnt_{d}"] += down[f"dqscorecnt_{d}"]
        if up[f"dqscorecnt_{d}"]:
            up[f"dqscore_{d}"] = up[f"dqscoresum_{d}"] / up[f"dqscorecnt_{d}"]


def affected_guids(changed: Iterable[str], docs: Dict[str, dict]) -> Set[str]:
    """Documents that can change when the given entities change: the entities, their derived relations and
    everything below them in a breadcrumb (names and parents propagate down)."""
    out: Set[str] = set(changed)
    for g in list(out):
        d = docs.get(g)
        if d:
            for base in RELATIONSHIP_MAP.values():
                out.update(d[f"{base}guid"])
    below = {g for g, d in docs.items() if out.intersection(d["breadcrumbguid"])}
    return out | below
