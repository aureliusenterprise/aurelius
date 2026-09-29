"""Phase 4: the lineage registration API (formerly m4i-lineage-rest-api) and the governance dashboard.

The contract test runs the payloads of ``data/lineage_api_cases.json`` through pyatlas' converters and compares
them with what the old service sent to Atlas for the same payloads (``data/lineage_api_reference.json``, recorded
by ``scripts/gen_lineage_api_spec.py`` from the old code)."""
import json
import os
import re

import pytest

from pyatlas.aurelius import lineage_api as la
from tests.conftest import _fresh_client

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ZIP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "m4i-atlas-post-install",
                   "data", "sample_data.zip")
V2 = "/api/atlas/v2"
LIN = "/api/lin_api"
CASES = {(c["ep"], c["name"]): c["payload"] for c in json.load(open(os.path.join(DATA, "lineage_api_cases.json")))}
REFERENCE = json.load(open(os.path.join(DATA, "lineage_api_reference.json")))
# where the old service answered 500, pyatlas answers properly (documented in lineage_api.py)
OLD_SERVICE_FAILED = {("entity/kafkaTopic_entity", "missing replicas"): 400}


def _renumber(body):
    mapping = {}

    def sub(m):
        g = m.group(1)
        if g == "-1":
            return m.group(0)
        mapping.setdefault(g, f"-g{len(mapping) + 1}")
        return f'"{mapping[g]}"'
    return json.loads(re.sub(r'"(-\d+)"', sub, json.dumps(body)))


def _entities_only(x):
    """typeName, guid, attributes (+ relationshipAttributes) of every entity; the old client's empty extras dropped."""
    if isinstance(x, dict):
        if {"typeName", "attributes", "guid"} <= set(x):
            out = {"typeName": x["typeName"], "guid": x["guid"],
                   "attributes": _entities_only({k: v for k, v in x["attributes"].items() if k != "unmappedAttributes"})}
            if x.get("relationshipAttributes"):
                out["relationshipAttributes"] = _entities_only(x["relationshipAttributes"])
            return out
        return {k: _entities_only(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_entities_only(v) for v in x]
    return x


@pytest.mark.parametrize("ref", REFERENCE, ids=[f"{r['ep']}:{r['name']}" for r in REFERENCE])
def test_same_atlas_entities_as_the_old_service(ref):
    payload = CASES[(ref["ep"], ref["name"])]
    if ref["status"] == 200:
        entities, referred = la.convert(ref["ep"], payload)
        mine = _entities_only(_renumber({"entities": entities, "referredEntities": referred}))
        assert mine == _entities_only(ref["atlas"])
    elif ref["status"] == 400:
        with pytest.raises(la.PayloadError) as e:
            la.convert(ref["ep"], payload)
        assert e.value.errors == ref["response"]["errors"]
    else:
        expected = OLD_SERVICE_FAILED[(ref["ep"], ref["name"])]
        with pytest.raises(la.PayloadError):
            la.convert(ref["ep"], payload)
        assert expected == 400


def test_every_namespace_has_a_contract_case():
    assert {r["ep"] for r in REFERENCE if r["status"] == 200} == set(la.NAMESPACES)
    assert la.qualified_name("My Cloud & Co", prefix="x") == "x--my-cloud-co"


def test_avro_types_outside_the_old_enum_are_kept():
    entities, referred = la.convert("entity/kafkaTopic_entity", {
        "name": "t", "cluster": "c", "environment": "e", "partitions": 1, "replicas": 1, "key_schema": "string",
        "value_schema": {"fields": [{"name": "flag", "type": "boolean", "doc": None},
                                    {"name": "tags", "type": {"type": "array", "items": "string"}, "doc": None}]}})
    types = {f["attributes"]["name"]: f["attributes"]["fieldType"] for f in entities[0]["attributes"]["fields"]}
    assert types == {"flag": "boolean", "tags": "record"}


@pytest.fixture
def client():
    c = _fresh_client()
    yield c
    c.__exit__(None, None, None)


def post(c, ns, payload, status=200):
    r = c.post(f"{LIN}/{ns}/", json=payload)
    assert r.status_code == status, r.text
    return r.json()


def entity_by_qn(c, type_name, qn):
    r = c.get(f"{V2}/entity/uniqueAttribute/type/{type_name}", params={"attr:qualifiedName": qn})
    assert r.status_code == 200, r.text
    return r.json()["entity"]


def test_registration_end_to_end(client):
    c = client
    # the Kubernetes landscape, top down (every object references its parent by qualified name)
    assert post(c, "kubernetes/kubernetes_environment", {"qualifiedName": "prod", "name": "Production",
                                                          "kubernetesClusters": []}) == {"CREATE": 1, "UPDATE": 0, "DELETE": 0}
    post(c, "kubernetes/kubernetes_cluster", {"qualifiedName": "prod--aks", "name": "AKS", "kubernetesEnvironment": "prod",
                                              "kubernetesNamespace": []})
    post(c, "kubernetes/kubernetes_namespace", {"qualifiedName": "prod--aks--orders", "name": "orders",
                                                "kubernetesCluster": "prod--aks", "kubernetesDeployment": [],
                                                "kubernetesCronjob": []})
    post(c, "kubernetes/kubernetes_deployment", {"qualifiedName": "orders-dep", "name": "orders",
                                                 "kubernetesNamespace": "prod--aks--orders", "kubernetesPod": []})
    post(c, "kubernetes/kubernetes_pod", {"qualifiedName": "orders-pod", "name": "orders-pod",
                                          "kubernetesDeployment": "orders-dep", "replicas": "2"})
    ns = entity_by_qn(c, "m4i_kubernetes_namespace", "prod--aks--orders")
    assert [r["displayText"] for r in ns["relationshipAttributes"]["kubernetesDeployment"]] == ["orders"]
    pod = entity_by_qn(c, "m4i_kubernetes_pod", "orders-pod")
    assert pod["attributes"]["replicas"] == "2"
    # datasets, then a process between them: lineage
    for qn in ("orders-in", "orders-out"):
        c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_dataset", "attributes": {"qualifiedName": qn, "name": qn}}})
    post(c, "process/microservice_process", {"qualifiedName": "orders-api", "name": "Orders API", "system": "orders-pod",
                                             "inputs": ["orders-in"], "outputs": ["orders-out"]})
    ms = entity_by_qn(c, "m4i_microservice_process", "orders-api")
    lineage = c.get(f"{V2}/lineage/{ms['guid']}", params={"direction": "BOTH", "depth": 3}).json()
    assert {e["attributes"]["qualifiedName"] for e in lineage["guidEntityMap"].values()} >= {"orders-in", "orders-out"}
    # registering again updates
    assert post(c, "process/microservice_process", {"qualifiedName": "orders-api", "name": "Orders API v2",
                                                    "system": "orders-pod", "inputs": ["orders-in"],
                                                    "outputs": ["orders-out"]})["UPDATE"] == 1
    assert entity_by_qn(c, "m4i_microservice_process", "orders-api")["attributes"]["name"] == "Orders API v2"
    # listing (subtypes included, as Atlas basic search): the microservice is a generic process too
    listed = c.get(f"{LIN}/process/generic_process/").json()
    assert listed == {"entities": 1, "qualifiedNames": ["orders-api"]}
    assert c.get(f"{LIN}/process/microservice_process/").json()["qualifiedNames"] == ["orders-api"]
    # connector processes work (the type was missing in Atlas)
    post(c, "process/connector_process", {"qualifiedName": "sink", "name": "Sink", "inputs": ["orders-out"],
                                          "outputs": ["orders-in"], "connectorType": "sink", "server": "connect"})
    assert entity_by_qn(c, "m4i_connector_process", "sink")["attributes"]["server"] == "connect"
    # errors: validation (old format), unknown reference (Atlas message), unknown namespace
    r = post(c, "process/generic_process", {"qualifiedName": "x", "name": "x", "inputs": []}, status=400)
    assert r["errors"] == {"inputs": "[] should be non-empty", "outputs": "'outputs' is a required property"}
    r = c.post(f"{LIN}/kubernetes/kubernetes_cluster/", json={"qualifiedName": "k", "name": "k",
                                                              "kubernetesEnvironment": "nope", "kubernetesNamespace": []})
    assert r.status_code == 404 and "nope" in r.json()["errorMessage"]
    assert c.get(f"{LIN}/process/nope/").status_code == 404


def test_kafka_topic_with_fields(client):
    c = client
    post(c, "entity/confluentCloud_entity", {"name": "Confluent"})
    post(c, "entity/confluentEnvironment_entity", {"name": "Dev", "confluent_cloud": "confluent", "schema_registry": True})
    post(c, "entity/kafkaCluster_entity", {"name": "Cluster A", "confluent_environment": "confluent--dev",
                                           "kafka_partitions": 3, "kafka_replicas": 2})
    for qn in ("crm--email", "orders--id"):
        c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_attribute", "attributes": {"qualifiedName": qn, "name": qn}}})
    counts = post(c, "entity/kafkaTopic_entity", {
        "name": "orders", "cluster": "cluster-a", "environment": "confluent--dev", "partitions": 3, "replicas": 2,
        "key_schema": "string", "value_schema": {"fields": [
            {"name": "id", "doc": "orders--id", "type": "string"},
            {"name": "customer", "doc": None, "type": ["null", {"name": "customer", "type": "record", "doc": None,
                                                              "fields": [{"name": "email", "doc": "crm--email", "type": "string"}]}]}]}})
    assert counts["CREATE"] == 6            # topic, collection, 4 fields (id, customer, customer record, email)
    topic = entity_by_qn(c, "m4i_kafka_topic", "confluent--dev--cluster-a--orders")
    assert sorted(f["displayText"] for f in topic["relationshipAttributes"]["fields"]) == ["customer", "id"]
    email = entity_by_qn(c, "m4i_kafka_field", "confluent--dev--cluster-a--orders--customer--customer--email")
    assert email["attributes"]["fieldType"] == "string"
    assert [a["displayText"] for a in email["relationshipAttributes"]["attributes"]] == ["crm--email"]
    coll = entity_by_qn(c, "m4i_collection", "confluent--dev--cluster-a--data")
    assert [s["displayText"] for s in coll["relationshipAttributes"]["systems"]] == ["Cluster A"]


def test_lineage_api_needs_a_login_and_write_access(client):
    c = client
    c.auth = ("rangertagsync", "rangertagsync")
    r = c.post(f"{LIN}/kubernetes/kubernetes_pod/", json={"qualifiedName": "p", "name": "p"})
    assert r.status_code == 403
    c.auth = None
    assert c.get(f"{LIN}/kubernetes/kubernetes_pod/").status_code == 401


@pytest.mark.skipif(not os.path.exists(ZIP), reason="Aurelius sample data not in the monorepo")
def test_governance_dashboard():
    c = _fresh_client(import_on_start=ZIP, import_on_start_mode="always")
    try:
        c.portal.call(c.app.state.services.aurelius.flush)
        d = c.get("/api/aurelius/data_governance_dashboard").json()
        assert d["totalNumberOfDomains"] == 9 and d["totalNumberOfActiveDomains"] == 7
        assert d["domains"]["Finance"] == {"name": "Finance", "guid": "6f3a7542-9f15-4753-bb19-65d29fcdc330",
                                           "isActive": True, "totalNumberOfEntities": 1}
        assert d["domains"]["Logistics"]["isActive"] is False
    finally:
        c.__exit__(None, None, None)
