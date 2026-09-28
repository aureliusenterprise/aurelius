import io
import time

from tests.helpers import create_sales_model

G = "/api/atlas/v2/glossary"


def _mk(client):
    g = client.post(G, json={"name": "Finance", "shortDescription": "finance terms"})
    assert g.status_code == 200, g.text
    g = g.json()
    assert g["qualifiedName"] == "Finance"
    t1 = client.post(f"{G}/term", json={"name": "Revenue", "anchor": {"glossaryGuid": g["guid"]},
                                        "shortDescription": "money in", "examples": ["sales"]})
    assert t1.status_code == 200, t1.text
    t1 = t1.json()
    t2 = client.post(f"{G}/term", json={"name": "Income", "anchor": {"glossaryGuid": g["guid"]},
                                        "synonyms": [{"termGuid": t1["guid"], "description": "same thing"}]}).json()
    return g, t1, t2


def test_glossary_crud_and_terms(client):
    g, t1, t2 = _mk(client)
    assert t1["qualifiedName"] == "Revenue@Finance"
    assert t1["anchor"]["glossaryGuid"] == g["guid"]
    assert t2["synonyms"][0]["termGuid"] == t1["guid"]
    # symmetric relation is visible from the other side too
    t1 = client.get(f"{G}/term/{t1['guid']}").json()
    assert t1["synonyms"][0]["termGuid"] == t2["guid"]
    assert t1["synonyms"][0]["description"] == "same thing"
    gl = client.get(f"{G}/{g['guid']}").json()
    assert sorted(t["displayText"] for t in gl["terms"]) == ["Income", "Revenue"]
    assert [x["name"] for x in client.get(G).json()] == ["Finance"]
    hdrs = client.get(f"{G}/{g['guid']}/terms/headers", params={"limit": 1, "sort": "DESC"}).json()
    assert [h["displayText"] for h in hdrs] == ["Revenue"]
    assert len(client.get(f"{G}/{g['guid']}/terms").json()) == 2
    det = client.get(f"{G}/{g['guid']}/detailed").json()
    assert set(det["termInfo"]) == {t1["guid"], t2["guid"]}
    rel = client.get(f"{G}/terms/{t2['guid']}/related").json()
    assert list(rel) == ["synonyms"]
    # duplicates / validation
    assert client.post(G, json={"name": "Finance"}).status_code == 409
    assert client.post(f"{G}/term", json={"name": "Revenue", "anchor": {"glossaryGuid": g["guid"]}}).status_code == 409
    assert client.post(f"{G}/term", json={"name": "a.b", "anchor": {"glossaryGuid": g["guid"]}}).json()["errorCode"] == "ATLAS-400-00-083"
    assert client.post(f"{G}/term", json={"name": "x"}).json()["errorCode"] == "ATLAS-400-00-072"
    # partial update and update removing relation
    r = client.put(f"{G}/term/{t2['guid']}/partial", json={"shortDescription": "earned"})
    assert r.status_code == 200 and r.json()["shortDescription"] == "earned" and r.json()["synonyms"]
    assert client.put(f"{G}/term/{t2['guid']}/partial", json={"bogus": "x"}).status_code == 400
    t2 = client.get(f"{G}/term/{t2['guid']}").json()
    t2.pop("synonyms")
    r = client.put(f"{G}/term/{t2['guid']}", json=t2)
    assert r.status_code == 200, r.text
    assert "synonyms" not in r.json()
    r = client.put(f"{G}/{g['guid']}/partial", json={"usage": "for finance"})
    assert r.json()["usage"] == "for finance"
    # glossary objects are internal types: not in normal search
    res = client.post("/api/atlas/v2/search/basic", json={"query": "Revenue"}).json()
    assert "entities" not in res


def test_categories_hierarchy(client):
    g, t1, t2 = _mk(client)
    parent = client.post(f"{G}/category", json={"name": "Metrics", "anchor": {"glossaryGuid": g["guid"]},
                                                  "terms": [{"termGuid": t1["guid"]}]}).json()
    assert parent["qualifiedName"] == "Metrics@Finance"
    child = client.post(f"{G}/category", json={"name": "Sales", "anchor": {"glossaryGuid": g["guid"]},
                                                 "parentCategory": {"categoryGuid": parent["guid"]}}).json()
    assert child["qualifiedName"] == "Sales.Metrics@Finance"
    assert child["parentCategory"]["categoryGuid"] == parent["guid"]
    rel = client.get(f"{G}/category/{parent['guid']}/related").json()
    assert [c["categoryGuid"] for c in rel["children"]] == [child["guid"]]
    assert client.get(f"{G}/category/{parent['guid']}/terms").json()[0]["termGuid"] == t1["guid"]
    assert client.get(f"{G}/term/{t1['guid']}").json()["categories"][0]["displayText"] == "Metrics"
    heads = client.get(f"{G}/{g['guid']}/categories/headers").json()
    assert {h["displayText"]: h.get("parentCategoryGuid") for h in heads} == {"Metrics": None, "Sales": parent["guid"]}
    # renaming the parent through a move: make child top-level again
    c = client.get(f"{G}/category/{child['guid']}").json()
    c.pop("parentCategory")
    c = client.put(f"{G}/category/{child['guid']}", json=c).json()
    assert c["qualifiedName"] == "Sales@Finance"
    assert client.delete(f"{G}/category/{parent['guid']}").status_code == 204
    assert client.get(f"{G}/category/{parent['guid']}").status_code == 404
    assert "categories" not in client.get(f"{G}/term/{t1['guid']}").json()


def test_term_assignment_meanings_and_search(client):
    client.post("/api/atlas/v2/types/typedefs", json={"classificationDefs": [{"name": "SENSITIVE"}]})
    g, t1, t2 = _mk(client)
    ga = create_sales_model(client)
    table = ga["-10"]
    r = client.post(f"{G}/terms/{t1['guid']}/assignedEntities", json=[{"guid": table}])
    assert r.status_code == 204, r.text
    ent = client.get(f"/api/atlas/v2/entity/guid/{table}").json()["entity"]
    assert ent["meanings"][0]["displayText"] == "Revenue"
    assigned = client.get(f"{G}/terms/{t1['guid']}/assignedEntities").json()
    assert [a["guid"] for a in assigned] == [table]
    res = client.post("/api/atlas/v2/search/basic", json={"typeName": "hive_table", "termName": "Revenue@Finance"}).json()
    assert [e["guid"] for e in res["entities"]] == [table]
    assert res["entities"][0]["meaningNames"] == ["Revenue"]
    # classification on the term propagates to the assigned entity
    client.post(f"/api/atlas/v2/entity/guid/{t1['guid']}/classifications", json=[{"typeName": "SENSITIVE"}])
    cls = client.get(f"/api/atlas/v2/entity/guid/{table}/classifications").json()["list"]
    assert [(c["typeName"], c["entityGuid"]) for c in cls] == [("SENSITIVE", t1["guid"])]
    # cannot delete an assigned term
    assert client.delete(f"{G}/term/{t1['guid']}").json()["errorCode"] == "ATLAS-400-00-084"
    # dissociation needs the relationship guid
    assert client.request("DELETE", f"{G}/terms/{t1['guid']}/assignedEntities", json=[{"guid": table}]).status_code == 400
    rel_guid = assigned[0]["relationshipGuid"]
    r = client.request("DELETE", f"{G}/terms/{t1['guid']}/assignedEntities",
                       json=[{"guid": table, "relationshipGuid": rel_guid}])
    assert r.status_code == 204
    assert "meanings" not in client.get(f"/api/atlas/v2/entity/guid/{table}").json()["entity"]
    assert client.get(f"/api/atlas/v2/entity/guid/{table}/classifications").json()["list"] == []
    assert client.delete(f"{G}/term/{t1['guid']}").status_code == 204
    assert client.delete(f"{G}/{g['guid']}").status_code == 204
    assert client.get(G).json() == []


def test_glossary_import_export_and_search(client):
    tpl = client.get(f"{G}/import/template")
    assert tpl.text.startswith("GlossaryName, TermName")
    csv_data = ("GlossaryName,TermName,ShortDescription,LongDescription,Examples,Abbreviation,Usage,AdditionalAttributes,"
                "TranslationTerms,ValidValuesFor,Synonyms\n"
                "HR,Employee,a worker,,e1|e2,EMP,,level:1,,,\n"
                "HR,Staff,workers,,,,,,,,HR:Employee\n"
                ",Broken,,,,,,,,,\n")
    r = client.post(f"{G}/import", files={"file": ("terms.csv", io.BytesIO(csv_data.encode()), "text/csv")})
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["successImportInfoList"]) == 2 and len(body["failedImportInfoList"]) == 1
    hr = client.get(G).json()[0]
    staff = next(t for t in client.get(f"{G}/{hr['guid']}/terms").json() if t["name"] == "Staff")
    assert staff["synonyms"][0]["displayText"] == "Employee"
    emp = next(t for t in client.get(f"{G}/{hr['guid']}/terms").json() if t["name"] == "Employee")
    assert emp["examples"] == ["e1", "e2"] and emp["additionalAttributes"] == {"level": "1"}
    s = client.post(f"{G}/search", json={"searchQuery": "work", "glossaryType": "TERM"}).json()
    assert s["approximateCount"] == 2 and len(s["glossary"][0]["terms"]) == 2
    assert client.post(f"{G}/download/create_file", json={"format": "CSV", "mode": "IMPORT_COMPATIBLE"}).status_code == 204
    for _ in range(50):
        st = client.get(f"{G}/download/status").json()["searchDownloadRecords"]
        if st and st[0]["status"] == "COMPLETE":
            break
        time.sleep(0.05)
    assert st[0]["status"] == "COMPLETE", st
    f = client.get(f"{G}/download/{st[0]['fileName']}")
    assert f.status_code == 200 and "Employee:ACTIVE" in f.content.decode("utf-8-sig")
