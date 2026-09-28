"""Generates ``models/9000-Aurelius/*.json`` from the m4i type definitions in ``libs/m4i-atlas-core``.

The Aurelius type definitions live as Python objects in m4i-atlas-core (``data_dictionary_types_def`` for the
data governance model, the connector / kubernetes / process defs for the lineage registration API).  pyatlas
loads Atlas-format JSON model files at startup, so this script converts them once; the JSON files are committed
and m4i-atlas-core is not a runtime dependency of pyatlas.

Run from the repository root with the m4i-atlas-core dependencies installed (dataclasses-json, aiohttp,
aiocache, pandas, python-keycloak)::

    python backend/pyatlas/scripts/gen_m4i_models.py

Re-run it whenever the type definitions in m4i-atlas-core change; ``tests/test_m4i_models.py`` fails when the
committed JSON and the Python definitions drift apart (if m4i-atlas-core is importable).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYATLAS = HERE.parent
REPO = PYATLAS.parent.parent
OUT = PYATLAS / "models" / "9000-Aurelius"
CATEGORIES = ("enumDefs", "structDefs", "classificationDefs", "entityDefs", "relationshipDefs", "businessMetadataDefs")
# volatile / server-assigned fields that do not belong in a model file
DROP = {"guid", "createTime", "createdBy", "updateTime", "updatedBy", "version", "dateFormatter", "updateType",
        "subTypes", "relationshipAttributeDefs", "businessAttributeDefs"}


def _clean(value):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in DROP or v is None:
                continue
            v = _clean(v)
            if v in ({}, []) and k not in ("attributeDefs", "superTypes", "entityTypes", "elementDefs"):
                continue
            out[k] = v
        return out
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


def _types_def_json(types_def) -> dict:
    d = json.loads(types_def.to_json())
    return {c: [_clean(x) for x in d.get(c) or []] for c in CATEGORIES}


# Where m4i-atlas-core (HEAD) and the types of the running Aurelius Atlas (atlas-typesdef.json of
# backend/m4i-atlas-post-install/data/sample_data.zip) differ, the deployed definition wins; found by
# tests/test_parity.py::test_m4i_models_match_the_typedefs_of_the_aurelius_sample_export.
_DEF = {"typeName": "string", "isOptional": True, "cardinality": "SINGLE", "valuesMinCount": 0, "valuesMaxCount": 1,
        "isUnique": False, "isIndexable": True, "includeInNotification": True, "searchWeight": 1,
        "indexType": "DEFAULT", "options": {}}
DEPLOYED_OVERRIDES = {
    # m4i-atlas-core has no "definition" on processes; the deployed type and the frontend have it
    ("m4i_generic_process", "definition"): {
        **_DEF, "name": "definition", "displayName": "Definition",
        "description": "The definition of the process determined by the process owner"},
    # m4i-atlas-core labels "definition" as "Data Type" and "fieldType" not at all
    ("m4i_field", "definition"): {"displayName": "Definition"},
    ("m4i_field", "fieldType"): {"displayName": "Field Type"},
}
# attribute properties Atlas does not keep on attributeDefs (they belong to relationship ends)
_NOT_STORED = ("relationshipTypeName", "isLegacyAttribute")


def _apply_overrides(d: dict) -> None:
    for e in d.get("entityDefs", []):
        attrs = e.setdefault("attributeDefs", [])
        for a in attrs:
            for k in _NOT_STORED:
                a.pop(k, None)
            patch = DEPLOYED_OVERRIDES.get((e["name"], a["name"]))
            if patch and "typeName" not in patch:          # a property change, not a new attribute
                a.update(patch)
        names = {a["name"] for a in attrs}
        for (t, n), a in DEPLOYED_OVERRIDES.items():
            if t == e["name"] and n not in names and "typeName" in a:
                attrs.insert(0, dict(a))


def load_sources() -> dict:
    """``{file stem: TypesDef dict}`` from m4i-atlas-core (imported from the monorepo's libs folder)."""
    sys.path.insert(0, str(REPO / "libs" / "m4i-atlas-core"))
    from m4i_atlas_core.entities.atlas.connectors import connectors_types_def
    from m4i_atlas_core.entities.atlas.data_dictionary import data_dictionary_types_def
    from m4i_atlas_core.entities.atlas.kubernetes import kubernetes_types_def
    from m4i_atlas_core.entities.atlas.m4i import m4i_types_def
    from m4i_atlas_core.entities.atlas.processes import process_types_def

    ordered = [("9010-m4i_data_dictionary_model", data_dictionary_types_def),
               ("9020-m4i_governance_model", m4i_types_def),
               ("9030-m4i_process_model", process_types_def),
               ("9040-m4i_connectors_model", connectors_types_def),
               ("9050-m4i_kubernetes_model", kubernetes_types_def)]
    seen: dict = {}
    result = {}
    for stem, td in ordered:
        d = _types_def_json(td)
        for c in CATEGORIES:
            unique = []
            for x in d[c]:
                prev = seen.get(x["name"])
                if prev is not None:
                    if prev != x:
                        raise SystemExit(f"type {x['name']} is defined differently in two m4i-atlas-core modules")
                    continue                     # defined in an earlier file already
                seen[x["name"]] = x
                unique.append(x)
            d[c] = unique
        d = copy.deepcopy(d)
        _apply_overrides(d)
        d = {c: v for c, v in d.items() if v}
        if d:
            result[stem] = d
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, d in load_sources().items():
        path = OUT / f"{stem}.json"
        path.write_text(json.dumps(d, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{path.relative_to(REPO)}: " + ", ".join(f"{len(v)} {k}" for k, v in d.items()))


if __name__ == "__main__":
    main()
