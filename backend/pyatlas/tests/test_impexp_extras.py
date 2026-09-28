"""Export/import details: incremental export, replication bookkeeping, import transforms/transformers,
startPosition, persisted admin tasks."""
import io
import json
import time
import zipfile

from tests.conftest import _fresh_client
from tests.helpers import create_sales_model

A = "/api/atlas/admin"
V2 = "/api/atlas/v2"
DB_ITEM = {"typeName": "hive_db", "uniqueAttributes": {"qualifiedName": "sales@cl1"}}


def _order(zip_bytes):
    return json.loads(zipfile.ZipFile(io.BytesIO(zip_bytes)).read("atlas-export-order.json"))


def _import(client, data, options=None):
    r = client.post(f"{A}/import", files={"data": ("e.zip", data, "application/zip")},
                    data={"request": json.dumps({"options": options or {}})})
    assert r.status_code == 200, r.text
    return r.json()


def _qn(client, guid):
    return client.get(f"{V2}/entity/guid/{guid}").json()["entity"]["attributes"]["qualifiedName"]


def test_incremental_export(client):
    ga = create_sales_model(client)
    full = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {"fetchType": "incremental",
                                                                                   "changeMarker": 0}})
    assert set(_order(full.content)) >= {ga["-1"], ga["-10"], ga["-20"], ga["-30"]}
    marker = json.loads(zipfile.ZipFile(io.BytesIO(full.content)).read("atlas-export-info.json"))["changeMarker"]
    assert marker > 0
    time.sleep(0.01)
    client.put(f"{V2}/entity/guid/{ga['-10']}", params={"name": "description"}, json="changed")
    inc = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {"fetchType": "incremental",
                                                                                  "changeMarker": marker}})
    assert inc.status_code == 200
    assert _order(inc.content) == [ga["-10"]]
    # the type definitions are still complete
    types = json.loads(zipfile.ZipFile(io.BytesIO(inc.content)).read("atlas-typesdef.json"))
    assert {"hive_db", "hive_table"} <= {d["name"] for d in types["entityDefs"]}


def test_replication_bookkeeping(client):
    ga = create_sales_model(client)
    r = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {"replicatedTo": "dc1$backup"}})
    assert r.status_code == 200
    marker = json.loads(zipfile.ZipFile(io.BytesIO(r.content)).read("atlas-export-info.json"))["changeMarker"]
    srv = client.get(f"{A}/server/backup").json()
    assert srv["fullName"] == "dc1$backup" and srv["name"] == "backup"
    assert json.loads(srv["additionalInfo"]["REPL_DETAILS"]) == {ga["-1"]: marker}
    assert client.get(f"{A}/server/pyatlas").status_code == 200          # the current server is registered too
    t = client.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
    assert t["attributes"]["replicatedTo"] == [{"guid": srv["guid"], "typeName": "AtlasServer"}]
    assert "replicatedTo" not in t["relationshipAttributes"]            # soft reference, no relationship
    audit = client.get(f"{A}/expimp/audit").json()
    assert audit[0]["operation"] == "EXPORT" and audit[0]["targetServerName"] == "backup"
    assert json.loads(audit[0]["resultSummary"])["operationStatus"] == "SUCCESS"

    other = _fresh_client()
    try:
        res = _import(other, r.content, {"replicatedFrom": "dc0$primary"})
        assert res["operationStatus"] == "SUCCESS"
        src = other.get(f"{A}/server/primary").json()
        t2 = other.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
        assert {"guid": src["guid"], "typeName": "AtlasServer"} in t2["attributes"]["replicatedFrom"]
        assert json.loads(src["additionalInfo"]["REPL_DETAILS"]) == {ga["-1"]: marker}
        assert other.get(f"{A}/expimp/audit").json()[0]["sourceServerName"] == "primary"
    finally:
        other.__exit__(None, None, None)

    # skipUpdateReplicationAttr: server marker only, entities untouched
    r = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {
        "replicatedTo": "dc1$archive", "skipUpdateReplicationAttr": "true"}})
    assert r.status_code == 200
    assert client.get(f"{A}/server/archive").status_code == 404
    t = client.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
    assert len(t["attributes"]["replicatedTo"]) == 1


def test_import_transforms_and_start_position(client):
    ga = create_sales_model(client)
    data = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {}}).content
    order = _order(data)

    other = _fresh_client()
    try:
        transforms = {"hive_table": {"qualifiedName": ["replace~@cl1~@cl2", "uppercase"],
                                     "*": ["addClassification~Imported"]},
                      "hive_db": {"*": ["addClassification~TopOnly~topLevel", "clearAttrValue~description"]},
                      "DataSet": {"owner": ["lowercase"]}}
        res = _import(other, data, {"transforms": json.dumps(transforms)})
        assert res["operationStatus"] == "SUCCESS", res
        assert _qn(other, ga["-10"]) == "SALES.CUSTOMERS@CL2"
        t = other.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
        assert "Imported" in [c["typeName"] for c in t["classifications"]]
        db = other.get(f"{V2}/entity/guid/{ga['-1']}").json()["entity"]
        assert [c["typeName"] for c in db["classifications"]] == ["TopOnly"]    # matches the exported item
        assert db["attributes"].get("description") is None
        assert other.get(f"{V2}/types/classificationdef/name/Imported").status_code == 200
    finally:
        other.__exit__(None, None, None)

    other = _fresh_client()
    try:
        transformers = [{"conditions": {"hive_db.clusterName": "EQUALS: cl1"},
                         "action": {"hive_db.clusterName": "SET: cl3"}},
                        {"conditions": {"hive_table.name": "STARTS_WITH_IGNORE_CASE: CUSTOMER_"},
                         "action": {"hive_table.name": "REPLACE_PREFIX: = :customer_=cust_"}}]
        res = _import(other, data, {"transformers": json.dumps(transformers)})
        assert res["operationStatus"] == "SUCCESS", res
        assert _qn(other, ga["-1"]) == "sales@cl3"
        assert _qn(other, ga["-10"]) == "sales.customers@cl3"
        assert _qn(other, ga["-20"]) == "sales.cust_summary@cl3"
        assert other.get(f"{V2}/entity/guid/{ga['-20']}").json()["entity"]["attributes"]["name"] == "cust_summary"
        assert _qn(other, ga["-10-c0"]) == "sales.customers.id@cl3"
        assert _qn(other, ga["-30"]) == "sales.summary_job@cl1"      # no handler for hive_process
    finally:
        other.__exit__(None, None, None)

    other = _fresh_client()
    try:
        res = _import(other, data, {"startPosition": str(len(order) - 1)})
        assert order[-1] in res["processedEntities"] and order[0] not in res["processedEntities"]
        assert other.get(f"{V2}/entity/guid/{order[0]}").status_code == 404
    finally:
        other.__exit__(None, None, None)


def test_ageout_tasks_are_listed_and_deletable(client):
    create_sales_model(client)
    tasks = client.post(f"{A}/audits/ageout", json={"auditAgingEnabled": True, "defaultAgeoutEnabled": True,
                                                    "defaultAgeoutAuditCount": 5}).json()
    assert tasks[0]["type"] == "AUDIT_REDUCTION_ENTITY_RETRIEVAL"
    assert tasks[0]["parameters"]["auditAgingType"] == "DEFAULT" and tasks[0]["createdBy"] == "admin"
    listed = client.get(f"{A}/tasks").json()
    assert tasks[0]["guid"] in {t["guid"] for t in listed}
    assert client.get(f"{A}/tasks", params={"guids": tasks[0]["guid"]}).json()[0]["status"] == "COMPLETE"
    assert client.delete(f"{A}/tasks", params={"guids": tasks[0]["guid"]}).status_code == 204
    assert tasks[0]["guid"] not in {t["guid"] for t in client.get(f"{A}/tasks").json()}


def test_soft_reference_attributes(client):
    ga = create_sales_model(client)
    srv = client.post(f"{V2}/entity", json={"entity": {"typeName": "AtlasServer", "attributes": {
        "name": "s1", "displayName": "s1", "fullName": "dc$s1"}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
    r = client.put(f"{V2}/entity/guid/{ga['-10']}", params={"name": "replicatedFrom"}, json=[f"AtlasServer:{srv}"])
    assert r.status_code == 200, r.text
    e = client.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
    assert e["attributes"]["replicatedFrom"] == [{"guid": srv, "typeName": "AtlasServer"}]
    assert "replicatedFrom" not in e["relationshipAttributes"]


def test_import_on_start_runs_once(client, tmp_path):
    create_sales_model(client)
    data = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {}}).content
    p = tmp_path / "demo.zip"
    p.write_bytes(data)
    other = _fresh_client(import_on_start=str(p))
    try:
        r = other.post(f"{V2}/search/basic", json={"typeName": "hive_table"}).json()
        assert r["approximateCount"] == 2
        ops = [a["operation"] for a in other.post(f"{A}/audits", json={}).json()]
        assert ops.count("IMPORT") == 1
        # a second start against the same store does not import again
        svc = other.app.state.services
        other.portal.call(svc.import_on_start)
        assert [a["operation"] for a in other.post(f"{A}/audits", json={}).json()].count("IMPORT") == 1
    finally:
        other.__exit__(None, None, None)


def test_import_on_start_always(client, tmp_path):
    create_sales_model(client)
    data = client.post(f"{A}/export", json={"itemsToExport": [DB_ITEM], "options": {}}).content
    p = tmp_path / "demo.zip"
    p.write_bytes(data)
    other = _fresh_client(import_on_start=str(p), import_on_start_mode="always")
    try:
        g = other.post(f"{V2}/search/basic", json={"typeName": "hive_db"}).json()["entities"][0]["guid"]
        other.put(f"{V2}/entity/guid/{g}", params={"name": "description"}, json="changed locally")
        other.portal.call(other.app.state.services.import_on_start)     # = next start
        assert [a["operation"] for a in other.post(f"{A}/audits", json={}).json()].count("IMPORT") == 2
        assert other.get(f"{V2}/entity/guid/{g}").json()["entity"]["attributes"]["description"] == "sales database"
    finally:
        other.__exit__(None, None, None)
