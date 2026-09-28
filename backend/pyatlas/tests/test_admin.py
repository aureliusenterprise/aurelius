import io
import json
import time
import zipfile

from tests.conftest import _fresh_client
from tests.helpers import create_sales_model

A = "/api/atlas/admin"
V2 = "/api/atlas/v2"


def _wait(fn, cond, timeout=60.0):
    """Poll until cond holds; background work against a real cluster can take several seconds."""
    deadline = time.time() + timeout
    while True:
        v = fn()
        if cond(v) or time.time() > deadline:
            return v
        time.sleep(0.05)


def test_export_import_roundtrip(client):
    client.post(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "Sensitive"}]})
    ga = create_sales_model(client)
    client.post(f"{V2}/entity/guid/{ga['-10']}/classifications", json=[{"typeName": "Sensitive"}])
    r = client.post(f"{A}/export", json={"itemsToExport": [{"typeName": "hive_db", "uniqueAttributes": {"qualifiedName": "sales@cl1"}}],
                                         "options": {"fetchType": "full"}})
    assert r.status_code == 200, r.text
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(z.namelist())
    assert {"atlas-export-info.json", "atlas-export-order.json", "atlas-typesdef.json"} <= names
    order = json.loads(z.read("atlas-export-order.json"))
    assert order[0] == ga["-1"] and ga["-30"] in order and ga["-20"] in order
    types = json.loads(z.read("atlas-typesdef.json"))
    assert "hive_table" in {d["name"] for d in types["entityDefs"]}
    assert "Sensitive" in {d["name"] for d in types["classificationDefs"]}
    info = json.loads(z.read("atlas-export-info.json"))
    assert info["operationStatus"] == "SUCCESS"

    other = _fresh_client()
    try:
        r = other.post(f"{A}/import", files={"data": ("export.zip", r.content, "application/zip")},
                       data={"request": "{}"})
        assert r.status_code == 200, r.text
        res = r.json()
        assert res["operationStatus"] == "SUCCESS", res
        assert set(res["processedEntities"]) >= {ga["-1"], ga["-10"], ga["-30"]}
        t = other.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]
        assert t["relationshipAttributes"]["db"]["guid"] == ga["-1"]
        assert len(t["relationshipAttributes"]["columns"]) == 2
        assert [c["typeName"] for c in t["classifications"]] == ["Sensitive"]
        # propagation was recomputed on the target
        cls = other.get(f"{V2}/entity/guid/{ga['-20']}/classifications").json()["list"]
        assert [(c["typeName"], c["entityGuid"]) for c in cls] == [("Sensitive", ga["-10"])]
        lin = other.get(f"{V2}/lineage/{ga['-20']}").json()
        assert len(lin["relations"]) == 2
        # import audits
        audits = other.post(f"{A}/audits", json={"auditFilters": {"attributeName": "operation", "operator": "eq",
                                                                   "attributeValue": "IMPORT"}}).json()
        assert audits and audits[0]["resultCount"] >= 8
        det = other.get(f"{A}/audit/{audits[0]['guid']}/details", params={"limit": 50}).json()
        assert ga["-10"] in {h["guid"] for h in det}
        assert other.get(f"{A}/expimp/audit").json()[0]["operation"] == "IMPORT"
        # re-import is idempotent
        r2 = other.post(f"{A}/import", files={"data": ("export.zip", z.fp.getvalue(), "application/zip")})
        assert r2.json()["operationStatus"] == "SUCCESS"
        assert other.post(f"{V2}/search/basic", json={"typeName": "hive_table"}).json()["approximateCount"] == 2
    finally:
        other.__exit__(None, None, None)


def test_connected_export_and_async_import(client):
    ga = create_sales_model(client)
    r = client.post(f"{A}/export", json={"itemsToExport": [{"guid": ga["-10"]}], "options": {"fetchType": "connected",
                                                                                             "skipLineage": "true"}})
    order = json.loads(zipfile.ZipFile(io.BytesIO(r.content)).read("atlas-export-order.json"))
    assert ga["-10"] in order and ga["-1"] in order and ga["-30"] not in order
    other = _fresh_client()
    try:
        req = other.post(f"{A}/async/import", files={"data": ("e.zip", r.content, "application/zip")},
                         data={"request": json.dumps({"options": {}})}).json()
        assert req["status"] in ("WAITING", "STAGING", "PROCESSING", "SUCCESSFUL")
        st = _wait(lambda: other.get(f"{A}/async/import/status/{req['importId']}").json(),
                   lambda v: v["status"] in ("SUCCESSFUL", "FAILED", "PARTIAL_SUCCESS"))
        assert st["status"] == "SUCCESSFUL", st
        assert st["importDetails"]["importProgress"] == 100.0
        lst = other.get(f"{A}/async/import/status").json()
        assert lst["list"][0]["importId"] == req["importId"]
    finally:
        other.__exit__(None, None, None)


def test_purge_audits_metrics_patches_misc(client):
    ga = create_sales_model(client)
    client.delete(f"{V2}/entity/guid/{ga['-20']}")
    r = client.put(f"{A}/purge", json=[ga["-20"], ga["-1"]]).json()
    assert {h["guid"] for h in r["mutatedEntities"]["PURGE"]} >= {ga["-20"]}
    summary_rows = client.post(f"{A}/audits", json={"auditFilters": {"attributeName": "operation", "operator": "eq",
                                                                      "attributeValue": "PURGE"}}).json()
    assert len(summary_rows) == 1 and summary_rows[0]["auditRowKind"] == "SUMMARY"
    s = client.get(f"{A}/audit/{summary_rows[0]['guid']}/summary").json()
    assert s["requestedCount"] == 2 and s["skippedCount"] >= 1
    assert len(client.get(f"{A}/audit/{summary_rows[0]['guid']}/batches").json()) == 1
    det = client.get(f"{A}/audit/{summary_rows[0]['guid']}/details").json()
    assert ga["-20"] in {h["guid"] for h in det}
    ops = {a["operation"] for a in client.post(f"{A}/audits", json={}).json()}
    assert {"SERVER_START", "PURGE"} <= ops
    client.post(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "X1"}]})
    assert client.post(f"{A}/audits", json={"auditFilters": {"attributeName": "operation", "operator": "eq",
                                                              "attributeValue": "TYPE_DEF_CREATE"}}).json()[0]["params"] == "X1"
    # metrics history
    client.portal.call(client.app.state.services.metrics_stats.save_now)
    stats = client.get(f"{A}/metricsstats").json()
    assert len(stats) == 1 and "metrics" not in stats[0]
    ct = stats[0]["collectionTime"]
    assert client.get(f"{A}/metricsstat/{ct}").json()["metrics"]["data"]["entity"]["entityActive"]["hive_table"] == 1
    ch = client.get(f"{A}/metricsstats/charts", params={"startTime": ct - 1, "endTime": ct + 1, "typeName": "hive_table"}).json()
    assert ch["hive_table"][0] == {"key": "Active", "values": [[ct, 1]]}
    rng = client.get(f"{A}/metricsstats/range", params={"startTime": ct - 1, "endTime": ct + 1, "typeName": "hive_table"}).json()
    assert rng[0]["typeData"]["hive_table"]["Active"] == 1
    # patches, debug metrics, stack, checkstate, index recovery
    p = client.get(f"{A}/patches").json()["patches"]
    assert any(x["status"] == "APPLIED" for x in p)
    dm = client.get(f"{A}/debug/metrics").json()
    assert any(v["numops"] >= 1 for v in dm.values())
    assert "MainThread" in client.get(f"{A}/stack").text
    cs = client.post(f"{A}/checkstate", json={"entityTypes": ["hive_column"]}).json()
    assert cs["entitiesScanned"] >= 2 and cs["state"] == "OK"
    assert client.post(f"{V2}/indexrecovery/start", params={"startTime": "2020-01-01T00:00:00.000Z"}).status_code == 204
    assert client.get(f"{V2}/indexrecovery").json()["customTime"].startswith("2020-01-01")
    assert client.get(f"{A}/activeSearches").json() == []
    # audit ageout: keep only the newest event per entity
    tasks = client.post(f"{A}/audits/ageout", json={"auditAgingEnabled": True, "defaultAgeoutEnabled": True,
                                                    "defaultAgeoutAuditCount": 1, "createEventsAgeoutAllowed": True}).json()
    assert tasks[0]["status"] == "COMPLETE"
    assert len(client.get(f"{V2}/entity/{ga['-10']}/audit").json()) == 1


def test_bm_import_relations_search_ondemand_lineage_and_downloads(client):
    client.post(f"{V2}/types/typedefs", json={"businessMetadataDefs": [{"name": "Ops", "attributeDefs": [
        {"name": "team", "typeName": "string", "options": {"applicableEntityTypes": '["DataSet"]', "maxStrLength": "50"}},
        {"name": "tags", "typeName": "array<string>", "options": {"applicableEntityTypes": '["DataSet"]', "maxStrLength": "50"}}]}]})
    ga = create_sales_model(client)
    csv_data = ("EntityType,EntityUniqueAttributeValue,BusinessAttributeName,BusinessAttributeValue\n"
                "hive_table,sales.customers@cl1,Ops.team,crm\n"
                "hive_table,sales.customers@cl1,Ops.tags,a|b\n"
                "hive_table,nope@cl1,Ops.team,x\n")
    r = client.post(f"{V2}/entity/businessmetadata/import", files={"file": ("bm.csv", io.BytesIO(csv_data.encode()), "text/csv")})
    assert r.status_code == 200, r.text
    assert len(r.json()["successImportInfoList"]) == 1 and len(r.json()["failedImportInfoList"]) == 1
    assert client.get(f"{V2}/entity/guid/{ga['-10']}").json()["entity"]["businessAttributes"] == {"Ops": {"team": "crm", "tags": ["a", "b"]}}
    # relationship search with filters on system attributes
    r = client.post(f"{V2}/search/relations", json={"relationshipName": "hive_table_columns", "limit": 10,
                                                     "relationshipFilters": {"attributeName": "end1Guid", "operator": "eq",
                                                                             "attributeValue": ga["-10"]}}).json()
    assert r["approximateCount"] == 2 and r["relations"][0]["end1"]["guid"] == ga["-10"]
    # on-demand lineage with limits
    r = client.post(f"{V2}/lineage/{ga['-20']}", json={ga["-20"]: {"direction": "INPUT", "inputRelationsLimit": 1, "depth": 3}}).json()
    assert {(x["fromEntityId"], x["toEntityId"]) for x in r["relations"]} == {(ga["-10"], ga["-30"]), (ga["-30"], ga["-20"])}
    assert r["lineageOnDemandPayload"][ga["-20"]]["inputRelationsLimit"] == 1
    # search result download
    assert client.post(f"{V2}/search/basic/download/create_file", json={
        "searchParameters": {"typeName": "hive_table"}, "attributeLabelMap": {"Qualified Name": "qualifiedName"}}).status_code == 204
    st = _wait(lambda: client.get(f"{V2}/search/download/status").json()["searchDownloadRecords"],
               lambda v: v and v[0]["status"] == "COMPLETE")
    f = client.get(f"{V2}/search/download/{st[0]['fileName']}").text
    assert '"Type name","Name","Classifications","Terms","Qualified Name","Owner","Description"' in f
    assert '"sales.customers@cl1"' in f
    assert client.post(f"{V2}/search/dsl/download/create_file", json={"searchParameters": {"query": "hive_column select name"}}).status_code == 204
    st = _wait(lambda: client.get(f"{V2}/search/download/status").json()["searchDownloadRecords"],
               lambda v: len(v) == 2 and all(x["status"] == "COMPLETE" for x in v))
    assert len(st) == 2
    assert client.get(f"{V2}/search/download/..%2Fetc").status_code in (400, 404)
