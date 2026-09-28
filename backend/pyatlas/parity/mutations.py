"""Check 3 - same changes, same results.

``run_scenario`` applies one fixed sequence of changes through the Atlas v2 REST API (works on Apache Atlas and
pyatlas alike) to a server that has the Aurelius (m4i) types.  All qualified names carry a run tag, so the
scenario can run repeatedly on the same server.  The result (a manifest) lists every touched entity with its
final state; ``compare_manifests`` compares two manifests guid-independently (by qualified name), and the
search/quality indices of both servers are then compared with ``parity indices --by-qualified-name``.

Steps (each exercises a propagation path the Flink jobs handle today):

 1. people, a domain with a domain lead, two data entities, attributes with steward and owner
 2. a system, collection, dataset and fields, a field linked to an attribute (field -> attribute breadcrumbs)
 3. rename the domain (breadcrumbs and derived names of every descendant change)
 4. move an attribute to the other data entity (parent replacement)
 5. change the business owner of a data entity
 6. add the PII classification to an attribute (classificationstext)
 7. make a data entity the child of the other (parentEntity / breadcrumb depth)
 8. delete a field (documents and quality results are removed)
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Callable, Dict, List, Optional, Tuple

from .canon import canonicalize
from .client import Client, ok
from .diff import Rules, diff
from .report import Report
from .store import normalize_entity

V2 = "/api/atlas/v2"


def _ref(type_name: str, qn: str) -> dict:
    return {"typeName": type_name, "uniqueAttributes": {"qualifiedName": qn}}


class Scenario:
    def __init__(self, client: Client, tag: Optional[str] = None, pause: float = 0.0):
        self.c = client
        self.tag = tag or uuid.uuid4().hex[:8]
        self.pause = pause
        self.touched: Dict[str, str] = {}          # qualifiedName -> typeName
        self.guids: Dict[str, str] = {}            # qualifiedName -> guid (deleted entities cannot be looked up)
        self.steps: List[dict] = []

    # ------------------------------------------------------------------ helpers
    def qn(self, *parts: str) -> str:
        return "--".join((f"parity{self.tag}",) + parts)

    def upsert(self, type_name: str, qn: str, attributes: dict, relationships: Optional[dict] = None) -> str:
        entity = {"typeName": type_name, "attributes": {"qualifiedName": qn, **attributes}}
        if relationships:
            entity["relationshipAttributes"] = relationships
        body = ok(self.c, "POST", f"{V2}/entity", json={"entity": entity})
        self.touched[qn] = type_name
        g = _guid_of(body, qn) or self.guid(type_name, qn)
        if g:
            self.guids[qn] = g
        return g

    def guid(self, type_name: str, qn: str) -> Optional[str]:
        status, body = self.c.request("GET", f"{V2}/entity/uniqueAttribute/type/{type_name}",
                                      params={"attr:qualifiedName": qn, "minExtInfo": "true"})
        return ((body or {}).get("entity") or {}).get("guid") if status == 200 else None

    def partial(self, type_name: str, qn: str, attributes: dict, relationships: Optional[dict] = None) -> None:
        """Full update of an existing entity (unique attribute lookup), keeping the other attributes."""
        status, body = self.c.request("GET", f"{V2}/entity/uniqueAttribute/type/{type_name}",
                                      params={"attr:qualifiedName": qn, "ignoreRelationships": "true"})
        if status != 200:
            raise RuntimeError(f"{self.c.name}: {type_name} {qn} not found ({status})")
        e = body["entity"]
        # keep the plain attributes; references are only sent where the step changes them
        plain = {k: v for k, v in (e.get("attributes") or {}).items() if not _has_ref(v)}
        entity = {"typeName": type_name, "guid": e["guid"], "attributes": {**plain, **attributes}}
        if relationships:
            entity["relationshipAttributes"] = relationships
        ok(self.c, "POST", f"{V2}/entity", json={"entity": entity})

    def step(self, name: str, fn: Callable[[], None]) -> None:
        started = time.time()
        fn()
        self.steps.append({"step": name, "seconds": round(time.time() - started, 3)})
        if self.pause:
            time.sleep(self.pause)

    # ------------------------------------------------------------------ the scenario
    def run(self) -> None:
        q = self.qn
        P = "m4i_person"
        dom, ent1, ent2 = q("dom"), q("dom", "ent1"), q("dom", "ent2")
        a1, a2, a3 = q("dom", "ent1", "attr1"), q("dom", "ent1", "attr2"), q("dom", "ent2", "attr3")
        sys_, coll, ds = q("sys"), q("sys", "coll"), q("sys", "coll", "ds")
        f1, f2 = q("sys", "coll", "ds", "field1"), q("sys", "coll", "ds", "field2")

        def base():
            for p in ("alice", "bob"):
                self.upsert(P, q(p), {"name": p.title(), "email": f"{p}.{self.tag}@example.com"})
            self.upsert("m4i_data_domain", dom, {"name": f"Domain {self.tag}", "definition": "parity domain"},
                        {"domainLead": [_ref(P, q("alice"))]})
            for e in (ent1, ent2):
                self.upsert("m4i_data_entity", e, {"name": e.rsplit("--", 1)[1], "definition": "parity entity"},
                            {"dataDomain": [_ref("m4i_data_domain", dom)], "businessOwner": [_ref(P, q("alice"))],
                             "steward": [_ref(P, q("bob"))]})
            for a, e in ((a1, ent1), (a2, ent1), (a3, ent2)):
                self.upsert("m4i_data_attribute", a, {"name": a.rsplit("--", 1)[1], "definition": "parity attribute",
                                                      "attributeType": "string"},
                            {"dataEntity": [_ref("m4i_data_entity", e)], "steward": [_ref(P, q("bob"))],
                             "businessOwner": [_ref(P, q("alice"))]})

        def technical():
            self.upsert("m4i_system", sys_, {"name": f"System {self.tag}"})
            self.upsert("m4i_collection", coll, {"name": "collection"}, {"systems": [_ref("m4i_system", sys_)]})
            self.upsert("m4i_dataset", ds, {"name": "dataset"}, {"collections": [_ref("m4i_collection", coll)]})
            self.upsert("m4i_field", f1, {"name": "field1", "fieldType": "string"},
                        {"datasets": [_ref("m4i_dataset", ds)], "attributes": [_ref("m4i_data_attribute", a1)]})
            self.upsert("m4i_field", f2, {"name": "field2", "fieldType": "int"},
                        {"datasets": [_ref("m4i_dataset", ds)], "attributes": [_ref("m4i_data_attribute", a3)]})

        def rename_domain():
            self.partial("m4i_data_domain", dom, {"name": f"Renamed domain {self.tag}"})

        def move_attribute():
            self.partial("m4i_data_attribute", a2, {}, {"dataEntity": [_ref("m4i_data_entity", ent2)]})

        def change_owner():
            self.partial("m4i_data_entity", ent1, {}, {"businessOwner": [_ref(P, q("bob"))]})

        def classify():
            g = self.guid("m4i_data_attribute", a1)
            ok(self.c, "POST", f"{V2}/entity/guid/{g}/classifications", json=[{"typeName": "PII"}])

        def reparent():
            self.partial("m4i_data_entity", ent2, {}, {"parentEntity": [_ref("m4i_data_entity", ent1)]})

        def delete_field():
            g = self.guid("m4i_field", f2)
            ok(self.c, "DELETE", f"{V2}/entity/guid/{g}")

        self.step("create business model", base)
        self.step("create technical model", technical)
        self.step("rename domain", rename_domain)
        self.step("move attribute", move_attribute)
        self.step("change business owner", change_owner)
        self.step("classify attribute", classify)
        self.step("reparent data entity", reparent)
        self.step("delete field", delete_field)

    # ------------------------------------------------------------------ result
    def manifest(self) -> dict:
        entities = {}
        for qn, t in sorted(self.touched.items()):
            status, body = self.c.request("GET", f"{V2}/entity/uniqueAttribute/type/{t}",
                                          params={"attr:qualifiedName": qn, "minExtInfo": "true"})
            entities[qn] = (body or {}).get("entity") if status == 200 else None
        return {"server": self.c.name, "tag": self.tag, "steps": self.steps, "guids": self.guids,
                "entities": entities}


def _has_ref(v) -> bool:
    first = v[0] if isinstance(v, list) and v else v
    return isinstance(first, dict) and ("guid" in first or "uniqueAttributes" in first)


def _guid_of(body: dict, qn: str) -> Optional[str]:
    for lst in ((body or {}).get("mutatedEntities") or {}).values():
        for h in lst:
            if (h.get("attributes") or {}).get("qualifiedName") == qn:
                return h.get("guid")
    return None


def run_scenario(client: Client, tag: Optional[str] = None, pause: float = 0.0) -> dict:
    s = Scenario(client, tag, pause)
    s.run()
    return s.manifest()


def _canonical(manifest: dict) -> Dict[str, Optional[dict]]:
    tag = manifest["tag"]
    guid_map = {g: qn.replace(f"parity{tag}", "parity<tag>") for qn, g in (manifest.get("guids") or {}).items()}
    for qn, e in manifest["entities"].items():
        if e:
            guid_map[e["guid"]] = qn.replace(f"parity{tag}", "parity<tag>")
    out = {}
    for qn, e in manifest["entities"].items():
        key = qn.replace(f"parity{tag}", "parity<tag>")
        if e is None:
            out[key] = None
            continue
        n = canonicalize(normalize_entity(e), guid_map)
        out[key] = json.loads(json.dumps(n).replace(f"parity{tag}", "parity<tag>").replace(tag, "<tag>"))
    return out


def compare_manifests(left: dict, right: dict, report: Optional[Report] = None) -> Report:
    report = report or Report("mutations", left.get("server", "left"), right.get("server", "right"))
    a, b = _canonical(left), _canonical(right)
    rules = Rules(unordered=["relationships.*", "attributes.*", "classifications", "labels"])
    for k in sorted(set(a) | set(b)):
        if k not in b:
            report.missing(k)
        elif k not in a:
            report.extra(k)
        elif (a[k] is None) != (b[k] is None):
            report.different(k, diff({"exists": a[k] is not None}, {"exists": b[k] is not None}))
        elif a[k] is not None:
            report.different(k, diff(a[k], b[k], rules))
        else:
            report.ok()
    report.stats.update({f"seconds {s['step']} (left/right)": f"{s['seconds']} / {t['seconds']}"
                         for s, t in zip(left.get("steps", []), right.get("steps", []))})
    return report


def tagged_guids(manifest: dict) -> List[Tuple[str, str]]:
    return [(e["guid"], qn) for qn, e in manifest["entities"].items() if e]
