"""Regenerates ``pyatlas/aurelius/lineage_api_spec.json`` and the contract reference of the lineage registration API
from the old service (``backend/m4i-lineage-rest-api``) and m4i-atlas-core.

Needs a Python environment in which the old service imports (flask<2.3, flask-restx, dataclasses-json, pandas,
pyjwt, cachetools, tenacity, sqlalchemy, flask-httpauth, aiohttp, aiocache, python-keycloak), e.g.

    python -m venv /tmp/linvenv && /tmp/linvenv/bin/pip install "flask<2.3" "werkzeug<2.3" flask-restx \\
        dataclasses-json pandas pyjwt cryptography cachetools tenacity sqlalchemy flask-httpauth flask-cors \\
        aiohttp aiocache python-keycloak
    /tmp/linvenv/bin/python backend/pyatlas/scripts/gen_lineage_api_spec.py

Writes the request schemas (the flask-restx models as JSON schema), which endpoints validate them, and the
attribute defaults of the m4i-atlas-core entity classes; then runs the old Flask app on
``tests/data/lineage_api_cases.json`` with Atlas replaced by a recorder and writes what it would have sent to
``tests/data/lineage_api_reference.json`` (negative guids renumbered in order of appearance).
"""
from __future__ import annotations

import dataclasses
import importlib
import json
import logging
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYATLAS = HERE.parent
REPO = PYATLAS.parent.parent
for p in (REPO / "libs" / "m4i-atlas-core", REPO / "libs" / "m4i-backend-core", REPO / "backend" / "m4i-lineage-rest-api"):
    sys.path.insert(0, str(p))
logging.disable(logging.CRITICAL)

from m4i_lineage_rest_api.app import flask_app  # noqa: E402
from m4i_lineage_rest_api.lin_api.restplus import api  # noqa: E402

SPEC = PYATLAS / "pyatlas" / "aurelius" / "lineage_api_spec.json"
CASES = PYATLAS / "tests" / "data" / "lineage_api_cases.json"
REFERENCE = PYATLAS / "tests" / "data" / "lineage_api_reference.json"
LIN_API = REPO / "backend" / "m4i-lineage-rest-api" / "m4i_lineage_rest_api" / "lin_api"


def camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(x[:1].upper() + x[1:] for x in parts[1:])


ATTRIBUTE_CLASSES: dict = {}


def _collect_attribute_classes(x) -> None:
    """Remember the attributes dataclass of every m4i-atlas-core entity object the old converters produced."""
    if dataclasses.is_dataclass(x) and hasattr(x, "type_name") and hasattr(x, "attributes"):
        ATTRIBUTE_CLASSES.setdefault(x.type_name, type(x.attributes))
        _collect_attribute_classes(x.attributes)
    elif dataclasses.is_dataclass(x):
        for f in dataclasses.fields(x):
            _collect_attribute_classes(getattr(x, f.name))
    elif isinstance(x, (list, tuple)):
        for v in x:
            _collect_attribute_classes(v)
    elif isinstance(x, dict):
        for v in x.values():
            _collect_attribute_classes(v)


def attribute_defaults(type_names):
    classes = dict(ATTRIBUTE_CLASSES)
    if "m4i_connector_process" not in classes:
        from m4i_atlas_core.entities.atlas.processes.ConnectorProcess import ConnectorProcessAttributes
        classes["m4i_connector_process"] = ConnectorProcessAttributes
    out = {}
    for t in sorted(type_names):
        d = {}
        for f in dataclasses.fields(classes[t]):
            if f.name == "unmapped_attributes":
                continue
            if f.default is not dataclasses.MISSING:
                d[camel(f.name)] = f.default
            elif f.default_factory is not dataclasses.MISSING:
                d[camel(f.name)] = f.default_factory()
            else:                       # required: always given; listed so that only known attributes are sent
                d[camel(f.name)] = None
        out[t] = dict(sorted(d.items()))
    return out


def main() -> None:
    fa = flask_app()
    fa.initialize_app()
    app = fa.app
    with app.test_request_context():
        swagger = api.__schema__
    validated = set()
    for f in LIN_API.rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r"api\.namespace\('([^']+)'", text)
        if m and "validate=True" in text:
            validated.add(m.group(1))
    endpoints = {}
    for path, ops in swagger["paths"].items():
        body = [x for x in ops.get("post", {}).get("parameters", []) if x.get("in") == "body"]
        ns = path.strip("/")
        endpoints[ns] = {"$ref": body[0]["schema"]["$ref"], "validate": ns in validated}

    reference = record(app, json.loads(CASES.read_text(encoding="utf-8")))
    types = set()

    def walk(x):
        if isinstance(x, dict):
            if {"typeName", "attributes", "guid"} <= set(x) and x["typeName"] != "m4i_collection":
                types.add(x["typeName"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk([r["atlas"] for r in reference])
    types |= {"m4i_connector_process"}
    spec = {"_generated_by": "backend/pyatlas/scripts/gen_lineage_api_spec.py",
            "endpoints": dict(sorted(endpoints.items())), "definitions": swagger["definitions"],
            "defaults": attribute_defaults(types)}
    SPEC.write_text(json.dumps(spec, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    REFERENCE.write_text(json.dumps(reference, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{SPEC}: {len(endpoints)} endpoints, {len(spec['defaults'])} types; {REFERENCE}: {len(reference)} cases")


def record(app, cases):
    from m4i_atlas_core import EntityMutationResponse
    from m4i_atlas_core.entities import EntitiesWithExtInfo
    captured = []

    async def fake_create_entities(*entities, referred_entities=None, access_token=None):
        _collect_attribute_classes(list(entities))
        _collect_attribute_classes(referred_entities or {})
        body = EntitiesWithExtInfo(entities=list(entities), referred_entities=referred_entities or {}).to_json()
        captured.append(json.loads(body))
        return EntityMutationResponse.from_dict({"mutatedEntities": {"CREATE": [{"guid": "g", "typeName": "t"}]
                                                                     * len(entities)}})
    for name, mod in list(sys.modules.items()):
        if name.startswith("m4i_lineage_rest_api") and hasattr(mod, "create_entities"):
            mod.create_entities = fake_create_entities

    # The old endpoint only worked when dataclasses_json failed to decode value_schema into its dataclass (it then
    # stayed the dict convert_to_atlas expects); for most schemas it crashed.  Record the intended behaviour.
    ktm = importlib.import_module("m4i_lineage_rest_api.lin_api.entity.kafkaTopic_entity.model.KafkaTopicApiModel")
    orig = ktm.KafkaTopicApiModel.from_dict.__func__

    def from_dict(cls, kvs, *a, **kw):
        obj = orig(cls, kvs, *a, **kw)
        raw = kvs.get("value_schema", kvs.get("valueSchema"))
        if isinstance(raw, dict):
            obj.value_schema = raw
        return obj
    ktm.KafkaTopicApiModel.from_dict = classmethod(from_dict)

    def normalize(body):
        mapping = {}

        def sub(m):
            g = m.group(1)
            if g == "-1":
                return m.group(0)
            mapping.setdefault(g, f"-g{len(mapping) + 1}")
            return f'"{mapping[g]}"'
        return json.loads(re.sub(r'"(-\d+)"', sub, json.dumps(body)))

    client = app.test_client()
    out = []
    for c in cases:
        captured.clear()
        # raw JSON: the test client's json= would sort the keys (Flask < 2.3), changing the order of fields
        r = client.post(f"/lin_api/{c['ep']}/", data=json.dumps(c["payload"]), content_type="application/json",
                        headers={"Authorization": "Bearer x"})
        out.append({"ep": c["ep"], "name": c["name"], "status": r.status_code, "response": r.get_json(silent=True),
                    "atlas": normalize(captured[0]) if captured else None})
    return out


if __name__ == "__main__":
    main()
