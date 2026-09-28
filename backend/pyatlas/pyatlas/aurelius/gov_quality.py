"""Governance quality (replaces the update-gov-data-quality Flink job and m4i-validate-entity).

The rules are the m4i-governance-data-quality definition files, one ``<type name>.json`` per entity type
(shipped in ``gov_rules/``, or ``PYATLAS_AURELIUS_GOV_RULES_DIR``).  A rule of type ``attribute`` runs on the
entity's ``attributes``, one of type ``relationship`` on its ``relationshipAttributes``; every active entity with
rules gets one document per rule in the ``atlas-dev-gov-quality`` engine, as the Flink job produced them:

    id = qualifiedname = "<entity guid>--<rule guid>", compliant = "1" | "0", usedattributes = the columns the rule reads, ...

Deleted entities have none.  :func:`validate` runs the same rules on an entity that is being edited (the
editor's ``validate_entity`` call) and answers per attribute, which the old service only mocked.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from . import quality_rules
from .engines import GOV_QUALITY

log = logging.getLogger("pyatlas.aurelius")

RULES_DIR = Path(__file__).parent / "gov_rules"


class GovRule(dict):
    """One rule definition (the JSON object of a definition file) plus its parsed expression."""

    @property
    def tree(self):
        return self["_tree"]


def load_rules(folder: Optional[str] = None) -> Dict[str, List[GovRule]]:
    """Rules per entity type name; rules with an invalid expression or ``active: 0`` are skipped (logged)."""
    path = Path(folder) if folder else RULES_DIR
    out: Dict[str, List[GovRule]] = {}
    for f in sorted(path.glob("*.json")):
        try:
            defs = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            log.error("governance quality rules %s: %s", f, e)
            continue
        for d in defs if isinstance(defs, list) else []:
            if not d.get("active", True):
                continue
            if d.get("type") not in ("attribute", "relationship") or not d.get("guid"):
                log.error("governance quality rule %s in %s: needs a guid and type attribute|relationship",
                          d.get("qualifiedName"), f.name)
                continue
            try:
                tree = quality_rules.parse(d.get("expression"))
            except quality_rules.RuleSyntaxError as e:
                log.error("governance quality rule %s in %s rejected: %s", d.get("qualifiedName"), f.name, e)
                continue
            out.setdefault(f.stem, []).append(GovRule(d, _tree=tree))
    return out


def _active(value):
    """Relationship attribute without references to deleted entities (Atlas keeps showing those, with
    ``relationshipStatus: DELETED``; the Flink job counted them, so a domain whose data entities were all deleted
    still "had" a data entity)."""
    def live(ref):
        return not (isinstance(ref, dict) and "DELETED" in (ref.get("relationshipStatus"), ref.get("entityStatus")))
    if isinstance(value, list):
        return [r for r in value if live(r)]
    return value if live(value) else None


def _row(entity: Mapping[str, Any], rule: GovRule) -> Mapping[str, Any]:
    if rule["type"] == "attribute":
        return entity.get("attributes") or {}
    return {k: _active(v) for k, v in (entity.get("relationshipAttributes") or {}).items()}


def score(entity: Mapping[str, Any], rule: GovRule) -> int:
    s = quality_rules.evaluate(rule.tree, quality_rules.Table([_row(entity, rule)])).get(0)
    return 1 if s else 0


def document(entity: Mapping[str, Any], rule: GovRule, compliant: int) -> dict:
    doc_id = f"{entity['guid']}--{rule['guid']}"
    return {
        "id": doc_id, "guid": rule["guid"], "name": rule.get("ruleTitle"), "qualifiedname": doc_id,
        "qualityqualifiedname": rule.get("qualifiedName"), "dataqualityruletypename": entity.get("typeName"),
        "dataqualitytype": rule["type"], "dataqualityruledescription": rule.get("ruleDescription"),
        "dataqualityruledimension": rule.get("qualityDimension"), "result_id": "0", "business_rule_id": "1",
        "compliant": str(compliant), "noncompliant_message": rule.get("noncompliantMessage"),
        "entity_guid": entity["guid"], "expression": rule.get("expression"),
        "usedattributes": quality_rules.used_attributes(rule["expression"]),
    }


def build_gov_documents(entities: Mapping[str, Mapping[str, Any]],
                        rules: Mapping[str, List[GovRule]]) -> Dict[str, dict]:
    docs: Dict[str, dict] = {}
    for e in entities.values():
        if e.get("status", "ACTIVE") != "ACTIVE" or not e.get("createTime"):
            continue
        for rule in rules.get(e.get("typeName"), ()):
            d = document(e, rule, score(e, rule))
            docs[d["id"]] = d
    return docs


# ------------------------------------------------------------------ validate_entity (editor preview)
def infer_type(body: Mapping[str, Any], rules: Mapping[str, List[GovRule]], reg) -> Optional[str]:
    """The editor also posts its raw form value ({attributes, relationshipAttributes, classifications}) without a
    type name: pick the rule type whose attributes cover all the form's fields, the closest fit first."""
    keys = set((body.get("attributes") or {}).keys()) | set((body.get("relationshipAttributes") or {}).keys())
    if not keys or reg is None:
        return None
    best, best_extra, tie = None, None, False
    for t in rules:
        et = reg.entities.get(t)
        if et is None:
            continue
        known = set(et.attributes) | set(et.relationship_attributes)
        if not keys <= known:
            continue
        extra = len(known - keys)
        if best_extra is None or extra < best_extra:
            best, best_extra, tie = t, extra, False
        elif extra == best_extra:
            tie = True
    return None if tie else best


def validate(body: Mapping[str, Any], rules: Mapping[str, List[GovRule]], reg=None) -> Dict[str, dict]:
    """``{attribute: {"items": [App Search style result], "isNonCompliant": bool}}`` for an entity with
    extended info ({entity, referredEntities}), a bare entity, or the editor's form value."""
    entity = body.get("entity") if isinstance(body.get("entity"), dict) else body
    type_name = entity.get("typeName") or infer_type(entity, rules, reg)
    out: Dict[str, dict] = {}
    for rule in rules.get(type_name or "", ()):
        compliant = score(entity, rule)
        rule_id = f"{entity.get('guid') or 'new'}--{rule['guid']}"
        item = {
            "id": {"raw": rule_id}, "name": {"raw": rule.get("ruleTitle")},
            "result": {"raw": rule.get("compliantMessage") if compliant else rule.get("noncompliantMessage")},
            "compliant": {"raw": str(compliant)}, "dataqualitytype": {"raw": rule["type"]},
            "dataqualityruledimension": {"raw": rule.get("qualityDimension")},
            "usedattributes": {"raw": quality_rules.used_attributes(rule["expression"])},
            "_meta": {"engine": GOV_QUALITY, "score": 1, "id": rule_id},
        }
        for attr in item["usedattributes"]["raw"]:
            entry = out.setdefault(attr, {"items": [], "isNonCompliant": False})
            entry["items"].append(item)
            entry["isNonCompliant"] = entry["isNonCompliant"] or not compliant
    return out

