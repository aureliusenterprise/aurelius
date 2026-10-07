"""Overview of a dataset: its lineage as a graph and its fields with the data dictionary behind them."""
import pytest

from tests.conftest import _fresh_client

V2 = "/api/atlas/v2"
A = "/api/aurelius/datasets"


@pytest.fixture()
def c():
    client = _fresh_client()
    try:
        yield client
    finally:
        client.__exit__(None, None, None)


def _create(c, type_name, name, attributes=None, relationships=None, classifications=()):
    body = {"entity": {"typeName": type_name,
                       "attributes": {"qualifiedName": name, "name": name, **(attributes or {})},
                       "relationshipAttributes": relationships or {},
                       "classifications": [{"typeName": t, "propagate": False} for t in classifications]}}
    r = c.post(f"{V2}/entity", json=body)
    assert r.status_code == 200, r.text
    m = r.json()["mutatedEntities"]
    return (m.get("CREATE") or m.get("UPDATE"))[0]["guid"]


def ref(guid, type_name):
    return {"guid": guid, "typeName": type_name}


@pytest.fixture()
def model(c):
    """Data entities Internal and External with the attribute Fullname; dataset src (fields NAME, RUN_ID) feeds
    the process load into dataset dst (no fields)."""
    internal = _create(c, "m4i_data_entity", "Internal")
    external = _create(c, "m4i_data_entity", "External")
    full_int = _create(c, "m4i_data_attribute", "Fullname", {"definition": "The full name of an employee."},
                       {"dataEntity": [ref(internal, "m4i_data_entity")]}, classifications=["PII"])
    full_ext = _create(c, "m4i_data_attribute", "Fullname@ext", {"name": "Fullname", "definition": "Full name."},
                       {"dataEntity": [ref(external, "m4i_data_entity")]})
    src = _create(c, "m4i_dataset", "src", {"definition": "source data"})
    dst = _create(c, "m4i_dataset", "dst")
    name = _create(c, "m4i_field", "src--NAME", {"name": "NAME", "fieldType": "text"},
                   {"datasets": [ref(src, "m4i_dataset")],
                    "attributes": [ref(full_int, "m4i_data_attribute"), ref(full_ext, "m4i_data_attribute")]})
    run = _create(c, "m4i_field", "src--RUN_ID", {"name": "RUN_ID", "fieldType": "keyword"},
                  {"datasets": [ref(src, "m4i_dataset")]})
    load = _create(c, "m4i_generic_process", "load",
                   {"inputs": [ref(src, "m4i_dataset")], "outputs": [ref(dst, "m4i_dataset")]})
    return dict(internal=internal, external=external, full_int=full_int, full_ext=full_ext, src=src, dst=dst,
                name=name, run=run, load=load)


def test_fields_with_attributes_descriptions_and_data_entities(c, model):
    r = c.get(f"{A}/{model['src']}/fields")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["dataset"]["name"] == "src" and body["dataset"]["definition"] == "source data"
    assert [f["name"] for f in body["fields"]] == ["NAME", "RUN_ID"]
    name, run = body["fields"]
    assert name["fieldType"] == "text" and name["guid"] == model["name"]
    attrs = name["attributes"]
    assert sorted((a["name"], tuple(e["name"] for e in a["dataEntities"])) for a in attrs) == \
        [("Fullname", ("External",)), ("Fullname", ("Internal",))]
    by_entity = {a["dataEntities"][0]["name"]: a for a in attrs}
    assert by_entity["Internal"]["definition"] == "The full name of an employee."
    assert by_entity["Internal"]["guid"] == model["full_int"]
    assert by_entity["Internal"]["dataEntities"][0]["guid"] == model["internal"]
    assert [c_["typeName"] for c_ in by_entity["Internal"]["classifications"]] == ["PII"]
    assert run["attributes"] == []
    assert body["summary"] == {"fields": 2, "withAttribute": 1, "withoutAttribute": 1, "attributes": 2,
                               "dataEntities": 2}


def test_inherited_classifications_are_marked(c, model):
    # PII of the attribute propagates to its field when propagation is on
    r = c.put(f"{V2}/entity/guid/{model['full_int']}/classifications",
              json=[{"typeName": "PII", "propagate": True}])
    assert r.status_code == 204, r.text
    name = next(f for f in c.get(f"{A}/{model['src']}/fields").json()["fields"] if f["name"] == "NAME")
    pii = [x for x in name["classifications"] if x["typeName"] == "PII"]
    assert pii and pii[0]["inherited"] is True and pii[0]["source"] == model["full_int"]


def test_lineage_graph_with_field_counts(c, model):
    r = c.get(f"{A}/{model['dst']}/lineage", params={"depth": 2})
    assert r.status_code == 200, r.text
    body = r.json()
    nodes = {n["guid"]: n for n in body["nodes"]}
    assert set(nodes) == {model["src"], model["load"], model["dst"]}
    assert nodes[model["load"]]["kind"] == "process" and nodes[model["load"]]["name"] == "load"
    assert nodes[model["src"]]["kind"] == "dataset" and nodes[model["src"]]["fieldCount"] == 2
    assert nodes[model["dst"]]["fieldCount"] == 0
    assert {(e["from"], e["to"]) for e in body["edges"]} == {(model["src"], model["load"]), (model["load"], model["dst"])}
    assert body["baseEntityGuid"] == model["dst"] and body["available"] is True


def test_lineage_of_a_dataset_without_lineage(c):
    alone = _create(c, "m4i_dataset", "alone")
    body = c.get(f"{A}/{alone}/lineage").json()
    assert [(n["name"], n["kind"], n["fieldCount"]) for n in body["nodes"]] == [("alone", "dataset", 0)]
    assert body["edges"] == [] and body["available"] is False


def test_lineage_that_cannot_be_determined_is_no_error(c, model, monkeypatch):
    async def broken(*args, **kwargs):
        raise RuntimeError("lineage store unavailable")

    from pyatlas.discovery.lineage import LineageService
    monkeypatch.setattr(LineageService, "lineage", broken)
    r = c.get(f"{A}/{model['src']}/lineage")
    assert r.status_code == 200, r.text
    body = r.json()
    assert [(n["name"], n["fieldCount"]) for n in body["nodes"]] == [("src", 2)]
    assert body["edges"] == [] and body["available"] is False
    # the base entity itself must exist
    assert c.get(f"{A}/no-such-guid/lineage").status_code == 404


def test_errors(c, model):
    assert c.get(f"{A}/{model['load']}/fields").status_code == 400          # not a dataset
    assert c.get(f"{A}/no-such-guid/fields").status_code == 404
    c.auth = None
    assert c.get(f"{A}/{model['src']}/fields").status_code == 401
