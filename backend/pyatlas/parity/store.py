"""Check 1 - stored data: an Atlas export ZIP (or a live Apache Atlas) against pyatlas.

Compared per entity (by guid): type, status, attributes, relationships (active related guids per
relationship attribute), direct classifications with their attributes, labels, business metadata and custom
attributes.  Propagated classifications are left out (Atlas recomputes them on import too).  Type definitions
of every type in the source are compared after removing server-assigned fields.  Entity counts per type are
reported as statistics.
"""
from __future__ import annotations

import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from .client import Client, ok
from .diff import Rules, diff
from .report import Report

V2 = "/api/atlas/v2"
TYPEDEF_CATEGORIES = ("enumDefs", "structDefs", "classificationDefs", "entityDefs", "relationshipDefs",
                      "businessMetadataDefs")
TYPEDEF_VOLATILE = {"guid", "createTime", "updateTime", "createdBy", "updatedBy", "version", "subTypes",
                    "relationshipAttributeDefs", "businessAttributeDefs", "dateFormatter", "typeVersion"}

DEFAULT_RULES = Rules(unordered=["labels", "classifications", "relationships.*", "attributes.*"])


# ---------------------------------------------------------------------------------------------- sources
class ZipSource:
    """An Atlas export ZIP (``atlas-export-order.json``, ``atlas-typesdef.json``, ``<guid>.json``)."""

    def __init__(self, path: str):
        self.path = path
        self.zip = zipfile.ZipFile(path)
        self.name = f"zip:{Path(path).name}"
        names = set(self.zip.namelist())
        self.order: List[str] = json.loads(self.zip.read("atlas-export-order.json")) \
            if "atlas-export-order.json" in names else \
            sorted(n[:-5] for n in names if n.endswith(".json") and not n.startswith("atlas-"))

    def typedefs(self) -> dict:
        try:
            return json.loads(self.zip.read("atlas-typesdef.json"))
        except KeyError:
            return {}

    def entities(self) -> Iterator[dict]:
        for g in self.order:
            try:
                doc = json.loads(self.zip.read(f"{g}.json"))
            except KeyError:
                continue
            yield doc.get("entity") or doc


class LiveSource:
    """A running Atlas / pyatlas; entities are enumerated per entity type with basic search."""

    def __init__(self, client: Client, types: Optional[Iterable[str]] = None, page: int = 100):
        self.client = client
        self.name = client.name
        self.types = list(types) if types else None
        self.page = page

    def typedefs(self) -> dict:
        return ok(self.client, "GET", f"{V2}/types/typedefs")

    def guids(self) -> Iterator[str]:
        types = self.types or [d["name"] for d in self.typedefs().get("entityDefs", [])
                               if not d["name"].startswith("__")]
        for t in types:
            offset = 0
            while True:
                body = ok(self.client, "POST", f"{V2}/search/basic", json={
                    "typeName": t, "excludeDeletedEntities": False, "includeSubTypes": False,
                    "limit": self.page, "offset": offset, "attributes": []})
                ents = (body or {}).get("entities") or []
                for e in ents:
                    yield e["guid"]
                if len(ents) < self.page:
                    break
                offset += self.page

    def entities(self) -> Iterator[dict]:
        for g in self.guids():
            e = fetch_entity(self.client, g)
            if e is not None:
                yield e


def fetch_entity(client: Client, guid: str) -> Optional[dict]:
    status, body = client.request("GET", f"{V2}/entity/guid/{guid}", params={"minExtInfo": "true"})
    if status == 404:
        return None
    if status // 100 != 2:
        raise RuntimeError(f"{client.name}: GET entity {guid} -> {status}: {str(body)[:300]}")
    return (body or {}).get("entity")


# ---------------------------------------------------------------------------------------------- normalizing
def _is_ref(v) -> bool:
    first = v[0] if isinstance(v, list) and v else v
    return isinstance(first, dict) and "guid" in first and ("typeName" in first or len(first) <= 3)


def _ref_guids(v) -> List[str]:
    items = v if isinstance(v, list) else [v]
    return sorted(x["guid"] for x in items if isinstance(x, dict) and x.get("guid")
                  and x.get("relationshipStatus", "ACTIVE") == "ACTIVE")


def normalize_entity(e: dict) -> dict:
    """The comparable content of an entity (server bookkeeping and propagated classifications removed)."""
    attrs = {}
    for k, v in (e.get("attributes") or {}).items():
        attrs[k] = _ref_guids(v) if _is_ref(v) else v
    rels = {}
    for k, v in (e.get("relationshipAttributes") or {}).items():
        g = _ref_guids(v) if v else []
        if g:
            rels[k] = g
    guid = e.get("guid")
    classifications = sorted(
        ({"typeName": c.get("typeName"), "attributes": c.get("attributes") or {},
          "propagate": c.get("propagate"), "validityPeriods": c.get("validityPeriods") or []}
         for c in e.get("classifications") or [] if c.get("entityGuid") in (None, guid)),
        key=lambda c: json.dumps(c, sort_keys=True, default=str))
    return {"typeName": e.get("typeName"), "status": e.get("status", "ACTIVE"), "attributes": attrs,
            "relationships": rels, "classifications": classifications, "labels": sorted(e.get("labels") or []),
            "businessAttributes": e.get("businessAttributes") or {},
            "customAttributes": e.get("customAttributes") or {}}


def normalize_typedef(d: dict) -> dict:
    out = {k: v for k, v in d.items() if k not in TYPEDEF_VOLATILE and v is not None}
    if isinstance(out.get("attributeDefs"), list):
        out["attributeDefs"] = {a.get("name", ""): _effective_counts({k: v for k, v in a.items() if v is not None})
                                for a in out["attributeDefs"]}
    for k in ("superTypes", "entityTypes"):
        if isinstance(out.get(k), list):
            out[k] = sorted(out[k])
    if isinstance(out.get("elementDefs"), list):
        out["elementDefs"] = sorted(out["elementDefs"], key=lambda x: (x.get("ordinal", 0), x.get("value", "")))
    return out


MAX_COUNT = 2147483647


def _effective_counts(a: dict) -> dict:
    """valuesMinCount / valuesMaxCount as Atlas enforces them (its multiplicity rules), so that "not set" (-1),
    0 and the explicit values mean the same on both sides."""
    optional = a.get("isOptional", True) is not False
    if a.get("cardinality", "SINGLE") == "SINGLE":
        a["valuesMinCount"], a["valuesMaxCount"] = (0 if optional else 1), 1
    else:
        mx, mn = a.get("valuesMaxCount"), a.get("valuesMinCount")
        a["valuesMaxCount"] = mx if isinstance(mx, int) and mx >= 2 else MAX_COUNT
        a["valuesMinCount"] = 0 if optional else max(1, mn if isinstance(mn, int) else 1)
    return a


def index_typedefs(td: dict) -> Dict[Tuple[str, str], dict]:
    return {(c, d["name"]): normalize_typedef(d) for c in TYPEDEF_CATEGORIES for d in td.get(c) or []}


# ---------------------------------------------------------------------------------------------- checks
def compare_typedefs(source_td: dict, target_td: dict, report: Report, rules: Optional[Rules] = None,
                     names: Optional[Iterable[str]] = None) -> None:
    rules = rules or Rules(unordered=["*.constraints", "*.attributeDefs.*.constraints"])
    src, tgt = index_typedefs(source_td), index_typedefs(target_td)
    wanted = set(names) if names is not None else None
    for key, d in sorted(src.items()):
        if wanted is not None and key[1] not in wanted:
            continue
        other = tgt.get(key)
        if other is None:
            report.missing(f"typedef {key[0]}:{key[1]}")
            continue
        report.different(f"typedef {key[0]}:{key[1]}", diff(d, other, rules))


def bundled_atlas_type_names() -> set:
    """Names of the types in Apache Atlas' own model files shipped with pyatlas (everything but 9000-Aurelius)."""
    out = set()
    models = Path(__file__).resolve().parent.parent / "models"
    for f in models.glob("*/*.json"):
        if f.parent.name.startswith("9000-"):
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        out.update(x["name"] for c in TYPEDEF_CATEGORIES for x in d.get(c) or [])
    return out


def typedef_names(td: dict, scope: str) -> Optional[set]:
    """``all`` -> None (every type), ``custom`` -> the source's types that are not Apache Atlas built-ins."""
    if scope == "all":
        return None
    builtin = bundled_atlas_type_names()
    return {d["name"] for c in TYPEDEF_CATEGORIES for d in td.get(c) or [] if d["name"] not in builtin}


def compare_store(source, target: Client, report: Optional[Report] = None, rules: Optional[Rules] = None,
                  with_typedefs: bool = True, limit: Optional[int] = None, typedef_scope: str = "custom") -> Report:
    """Compares every entity of ``source`` (:class:`ZipSource` / :class:`LiveSource`) with ``target``."""
    report = report or Report("store", source.name, target.name)
    rules = DEFAULT_RULES.merged(rules) if rules else DEFAULT_RULES
    counts: Counter = Counter()
    if with_typedefs:
        td = source.typedefs()
        names = typedef_names(td, typedef_scope)
        compare_typedefs(td, ok(target, "GET", f"{V2}/types/typedefs"), report, names=names)
        if names is not None:
            report.notes.append(f"type definitions compared: {len(names)} non-Atlas types "
                                "(use --typedefs all to include the Apache Atlas built-in types)")
    for i, exp in enumerate(source.entities()):
        if limit is not None and i >= limit:
            report.notes.append(f"stopped after {limit} entities (--limit)")
            break
        guid = exp.get("guid")
        counts[exp.get("typeName")] += 1
        try:
            got = fetch_entity(target, guid)
        except Exception as e:  # noqa: BLE001 - reported, the run goes on
            report.error(guid, str(e))
            continue
        if got is None:
            report.missing(guid, f"{exp.get('typeName')} {(exp.get('attributes') or {}).get('qualifiedName')}")
            continue
        report.different(guid, diff(normalize_entity(exp), normalize_entity(got), rules))
    report.stats.update({f"entities {t}": n for t, n in sorted(counts.items())})
    report.stats["entities total"] = sum(counts.values())
    report.stats.update(target_counts(target, counts))
    return report


def target_counts(target: Client, source_counts: Counter) -> Dict[str, str]:
    """Active entity counts per type on the target (basic search, own type only) next to the source count."""
    out = {}
    for t, n in sorted(source_counts.items()):
        status, body = target.request("POST", f"{V2}/search/basic", json={
            "typeName": t, "excludeDeletedEntities": False, "includeSubTypes": False, "limit": 1})
        if status // 100 == 2 and isinstance(body, dict):
            c = body.get("approximateCount")
            if isinstance(c, int) and c >= 0 and c != n:
                out[f"count {t} (source vs target)"] = f"{n} vs {c}"
    return out
