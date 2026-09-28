from tests.helpers import create_sales_model, hive_db

API = "/api/atlas/v2"


def qn(client, type_name, qualified_name):
    r = client.get(f"{API}/entity/uniqueAttribute/type/{type_name}", params={"attr:qualifiedName": qualified_name})
    assert r.status_code == 200, r.text
    return r.json()["entity"]


# ------------------------------------------------------------------ types
def test_builtin_models_loaded(client):
    r = client.get(f"{API}/types/typedefs/headers", params={"excludeInternalTypesAndReferences": "true"})
    names = {h["name"] for h in r.json()}
    assert {"hive_table", "DataSet", "Process", "hive_table_columns"} <= names
    assert not any(n.startswith("__") for n in names)
    d = client.get(f"{API}/types/entitydef/name/hive_table").json()
    assert "DataSet" in d["superTypes"]
    rel_attrs = {a["name"]: a for a in d["relationshipAttributeDefs"]}
    assert rel_attrs["columns"]["relationshipTypeName"] == "hive_table_columns"
    assert client.get(f"{API}/types/entitydef/name/hive_table_columns").status_code == 404


def test_typedef_crud(client):
    body = {"classificationDefs": [{"name": "Sensitive", "attributeDefs": [
        {"name": "level", "typeName": "int", "isOptional": True}]}],
        "entityDefs": [{"name": "my_dataset", "superTypes": ["DataSet"], "attributeDefs": [
            {"name": "rows", "typeName": "long"}]}],
        "enumDefs": [{"name": "my_enum", "elementDefs": [{"value": "A"}, {"value": "B"}]}]}
    r = client.post(f"{API}/types/typedefs", json=body)
    assert r.status_code == 200, r.text
    assert r.json()["classificationDefs"][0]["guid"]
    assert client.post(f"{API}/types/typedefs", json=body).json()["errorCode"] == "ATLAS-409-00-001"
    d = client.get(f"{API}/types/typedef/name/my_dataset").json()
    d["attributeDefs"].append({"name": "owner2", "typeName": "string"})
    r = client.put(f"{API}/types/typedefs", json={"entityDefs": [d]})
    assert r.status_code == 200, r.text
    assert r.json()["entityDefs"][0]["version"] == 2
    bad = {"entityDefs": [{"name": "broken", "superTypes": ["NoSuchType"]}]}
    assert client.post(f"{API}/types/typedefs", json=bad).status_code == 400
    # in use -> cannot delete
    client.post(f"{API}/entity", json={"entity": {"typeName": "my_dataset",
                                                   "attributes": {"qualifiedName": "x", "name": "x", "rows": 5}}})
    r = client.delete(f"{API}/types/typedef/name/my_dataset")
    assert r.status_code == 409
    assert client.delete(f"{API}/types/typedef/name/my_enum").status_code == 204
    assert client.get(f"{API}/types/enumdef/name/my_enum").status_code == 404


# ------------------------------------------------------------------ entities
def test_create_and_get_entities(client):
    ga = create_sales_model(client)
    t = client.get(f"{API}/entity/guid/{ga['-10']}").json()
    ent = t["entity"]
    assert ent["attributes"]["name"] == "customers"
    assert ent["relationshipAttributes"]["db"]["guid"] == ga["-1"]
    assert {c["displayText"] for c in ent["relationshipAttributes"]["columns"]} == {"id", "email"}
    assert set(t["referredEntities"]) == {ga["-10-c0"], ga["-10-c1"]}
    assert ent["relationshipAttributes"]["outputFromProcesses"] == []
    assert ent["relationshipAttributes"]["inputToProcesses"][0]["guid"] == ga["-30"]
    db = qn(client, "hive_db", "sales@cl1")
    assert len(db["relationshipAttributes"]["tables"]) == 2
    col = qn(client, "hive_column", "sales.customers.id@cl1")
    assert col["relationshipAttributes"]["table"]["guid"] == ga["-10"]
    assert col["attributes"]["position"] == 0
    # lookup through a super type
    assert qn(client, "DataSet", "sales.customers@cl1")["guid"] == ga["-10"]
    hdr = client.get(f"{API}/entity/guid/{ga['-10']}/header").json()
    assert hdr["displayText"] == "customers" and hdr["attributes"]["qualifiedName"] == "sales.customers@cl1"


def test_update_is_idempotent_and_detects_changes(client):
    create_sales_model(client)
    db = hive_db()
    r = client.post(f"{API}/entity", json={"entity": db}).json()
    assert "mutatedEntities" not in r or "UPDATE" not in r.get("mutatedEntities", {})
    db["attributes"]["description"] = "changed"
    r = client.post(f"{API}/entity", json={"entity": db}).json()
    assert r["mutatedEntities"]["UPDATE"][0]["attributes"]["qualifiedName"] == "sales@cl1"
    e = qn(client, "hive_db", "sales@cl1")
    assert e["attributes"]["description"] == "changed" and e["version"] == 1


def test_mandatory_and_invalid_values(client):
    r = client.post(f"{API}/entity", json={"entity": {"typeName": "hive_db", "attributes": {"qualifiedName": "a@b", "name": "a"}}})
    assert r.status_code == 400 and r.json()["errorCode"] == "ATLAS-400-00-02B"
    r = client.post(f"{API}/entity", json={"entity": {"typeName": "hive_column", "attributes": {
        "qualifiedName": "c", "name": "c", "type": "int", "position": "notanumber"}}})
    assert r.status_code == 400
    r = client.post(f"{API}/entity", json={"entity": {"typeName": "nope", "attributes": {}}})
    assert r.status_code == 404


def test_partial_update_and_unique_update(client):
    ga = create_sales_model(client)
    r = client.put(f"{API}/entity/guid/{ga['-10']}", params={"name": "description"}, json="customer master")
    assert r.status_code == 200, r.text
    assert client.get(f"{API}/entity/guid/{ga['-10']}").json()["entity"]["attributes"]["description"] == "customer master"
    r = client.put(f"{API}/entity/uniqueAttribute/type/hive_table", params={"attr:qualifiedName": "sales.customers@cl1"},
                   json={"entity": {"typeName": "hive_table", "attributes": {"comment": "hello"}}})
    assert r.status_code == 200, r.text
    assert r.json()["mutatedEntities"]["PARTIAL_UPDATE"][0]["guid"] == ga["-10"]
    ent = client.get(f"{API}/entity/guid/{ga['-10']}").json()["entity"]
    assert ent["attributes"]["comment"] == "hello" and ent["attributes"]["description"] == "customer master"
    assert len(ent["relationshipAttributes"]["columns"]) == 2  # untouched by partial update


def test_changing_relationship_and_composition_cascade(client):
    ga = create_sales_model(client)
    # full update of the table with only one column -> the other column is deleted (composition)
    r = client.post(f"{API}/entity", json={"entity": {
        "typeName": "hive_table", "attributes": {"qualifiedName": "sales.customers@cl1", "name": "customers"},
        "relationshipAttributes": {"columns": [{"guid": ga["-10-c0"]}]}}})
    assert r.status_code == 200, r.text
    assert client.get(f"{API}/entity/guid/{ga['-10-c1']}").json()["entity"]["status"] == "DELETED"
    cols = client.get(f"{API}/entity/guid/{ga['-10']}").json()["entity"]["relationshipAttributes"]["columns"]
    assert [c["guid"] for c in cols if c["relationshipStatus"] == "ACTIVE"] == [ga["-10-c0"]]
    # delete the table -> remaining column deleted as well, db keeps a deleted reference
    r = client.delete(f"{API}/entity/guid/{ga['-10']}").json()
    deleted = {h["guid"] for h in r["mutatedEntities"]["DELETE"]}
    assert deleted == {ga["-10"], ga["-10-c0"]}
    db = qn(client, "hive_db", "sales@cl1")
    statuses = {t["guid"]: t["entityStatus"] for t in db["relationshipAttributes"]["tables"]}
    assert statuses[ga["-10"]] == "DELETED"
    # unique value can be reused after delete
    r = client.post(f"{API}/entity", json={"entity": {"typeName": "hive_table", "attributes": {
        "qualifiedName": "sales.customers@cl1", "name": "customers"}, "relationshipAttributes": {"db": {"guid": ga["-1"]}}}})
    assert r.json()["mutatedEntities"]["CREATE"][0]["guid"] != ga["-10"]
    # purge
    r = client.put("/api/atlas/admin/purge", json=[ga["-10"]])
    assert r.json()["mutatedEntities"]["PURGE"][0]["guid"] == ga["-10"]
    assert client.get(f"{API}/entity/guid/{ga['-10']}").status_code == 404


def test_classifications_and_propagation(client):
    client.post(f"{API}/types/typedefs", json={"classificationDefs": [
        {"name": "Sensitive", "attributeDefs": [{"name": "level", "typeName": "int"}]}]})
    ga = create_sales_model(client)
    src, proc, dst = ga["-10"], ga["-30"], ga["-20"]
    r = client.post(f"{API}/entity/guid/{src}/classifications", json=[{"typeName": "Sensitive", "attributes": {"level": 3}}])
    assert r.status_code == 204, r.text
    # propagated table -> process -> table
    for g in (proc, dst):
        cls = client.get(f"{API}/entity/guid/{g}/classifications").json()["list"]
        assert [(c["typeName"], c["entityGuid"]) for c in cls] == [("Sensitive", src)], g
    r = client.post(f"{API}/entity/guid/{src}/classifications", json=[{"typeName": "Sensitive"}])
    assert r.status_code == 400
    # cannot delete propagated from target
    r = client.delete(f"{API}/entity/guid/{dst}/classification/Sensitive")
    assert r.json()["errorCode"] == "ATLAS-400-00-06C"
    # update propagates attribute changes
    client.put(f"{API}/entity/guid/{src}/classifications", json=[{"typeName": "Sensitive", "attributes": {"level": 5}}])
    cls = client.get(f"{API}/entity/guid/{dst}/classifications").json()["list"]
    assert cls[0]["attributes"]["level"] == 5
    # searching by classification includes propagated
    r = client.post(f"{API}/search/basic", json={"classification": "Sensitive", "typeName": "hive_table"}).json()
    assert {e["guid"] for e in r["entities"]} == {src, dst}
    # removing the lineage edge removes propagation downstream
    proc_ent = client.get(f"{API}/entity/guid/{proc}").json()["entity"]
    proc_ent["relationshipAttributes"] = {"inputs": [], "outputs": [{"guid": dst}]}
    r = client.post(f"{API}/entity", json={"entity": proc_ent})
    assert r.status_code == 200, r.text
    assert client.get(f"{API}/entity/guid/{dst}/classifications").json()["list"] == []
    # direct delete
    assert client.delete(f"{API}/entity/guid/{src}/classification/Sensitive").status_code == 204
    assert client.get(f"{API}/entity/guid/{src}/classifications").json()["list"] == []


def test_propagation_blocked_by_propagate_false(client):
    client.post(f"{API}/types/typedefs", json={"classificationDefs": [{"name": "SENSITIVE"}]})
    ga = create_sales_model(client)
    client.post(f"{API}/entity/guid/{ga['-10']}/classifications", json=[{"typeName": "SENSITIVE", "propagate": False}])
    assert client.get(f"{API}/entity/guid/{ga['-20']}/classifications").json()["list"] == []


def test_lineage(client):
    ga = create_sales_model(client)
    r = client.get(f"{API}/lineage/{ga['-20']}", params={"direction": "INPUT", "depth": 3})
    assert r.status_code == 200, r.text
    lin = r.json()
    edges = {(x["fromEntityId"], x["toEntityId"]) for x in lin["relations"]}
    assert edges == {(ga["-10"], ga["-30"]), (ga["-30"], ga["-20"])}
    assert set(lin["guidEntityMap"]) == {ga["-10"], ga["-20"], ga["-30"]}
    out = client.get(f"{API}/lineage/{ga['-10']}", params={"direction": "OUTPUT"}).json()
    assert {(x["fromEntityId"], x["toEntityId"]) for x in out["relations"]} == edges
    both = client.get(f"{API}/lineage/uniqueAttribute/type/hive_process",
                      params={"attr:qualifiedName": "sales.summary_job@cl1"}).json()
    assert {(x["fromEntityId"], x["toEntityId"]) for x in both["relations"]} == edges
    hidden = client.get(f"{API}/lineage/{ga['-20']}", params={"hideProcess": "true"}).json()
    assert [(x["fromEntityId"], x["toEntityId"]) for x in hidden["relations"]] == [(ga["-10"], ga["-20"])]
    assert client.get(f"{API}/lineage/{ga['-1']}").status_code == 404  # hive_db is not a lineage type


# ------------------------------------------------------------------ search
def test_basic_search(client):
    ga = create_sales_model(client)
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_table", "excludeDeletedEntities": True}).json()
    assert r["approximateCount"] == 2
    assert [e["displayText"] for e in r["entities"]] == ["customer_summary", "customers"]
    r = client.post(f"{API}/search/basic", json={"typeName": "DataSet", "entityFilters": {
        "condition": "AND", "criterion": [{"attributeName": "name", "operator": "startsWith", "attributeValue": "CUST"},
                                          {"attributeName": "owner", "operator": "=", "attributeValue": "etl"}]}}).json()
    assert r["approximateCount"] == 2
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_column", "entityFilters": {
        "attributeName": "position", "operator": ">", "attributeValue": "0"}, "sortBy": "name"}).json()
    assert [e["displayText"] for e in r["entities"]] == ["cnt", "email"]
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_table", "entityFilters": {
        "attributeName": "createTime", "operator": "timerange", "attributeValue": "1699999999000,1700000000001"}}).json()
    assert r["approximateCount"] == 2
    r = client.post(f"{API}/search/basic", json={"query": "summary", "typeName": "hive_table"}).json()
    assert [e["guid"] for e in r["entities"]] == [ga["-20"]]
    r = client.get(f"{API}/search/basic", params={"typeName": "hive_db", "attributes": "name"}).json()
    assert r["entities"][0]["attributes"]["name"] == "sales"
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_table", "attributes": ["db"]}).json()
    assert r["entities"][0]["attributes"]["db"]["guid"] == ga["-1"]
    assert client.post(f"{API}/search/basic", json={}).status_code == 400
    assert client.post(f"{API}/search/basic", json={"typeName": "nope"}).status_code == 400


def test_quick_search_relationship_search_and_suggestions(client):
    ga = create_sales_model(client)
    r = client.get(f"{API}/search/quick", params={"query": "customers"}).json()
    assert ga["-10"] in {e["guid"] for e in r["searchResults"]["entities"]}
    assert any(a["name"] == "hive_table" for a in r["aggregationMetrics"]["__typeName"])
    r = client.get(f"{API}/search/relationship", params={"guid": ga["-10"], "relation": "columns", "sortBy": "name",
                                                          "getApproximateCount": "true"}).json()
    assert [e["displayText"] for e in r["entities"]] == ["email", "id"] and r["approximateCount"] == 2
    r = client.get(f"{API}/search/suggestions", params={"prefixString": "cust"}).json()
    assert "customers" in r["suggestions"]
    r = client.get(f"{API}/search/attribute", params={"attrName": "qualifiedName", "attrValuePrefix": "sales.cust",
                                                      "typeName": "hive_table"}).json()
    assert r["approximateCount"] == 2
    r = client.get(f"{API}/search/fulltext", params={"query": "email"}).json()
    assert r["fullTextResult"][0]["entity"]["guid"] == ga["-10-c1"]


def test_dsl_subset(client):
    create_sales_model(client)
    r = client.get(f"{API}/search/dsl", params={"query": "hive_table where name = 'customers'"}).json()
    assert [e["displayText"] for e in r["entities"]] == ["customers"]
    r = client.get(f"{API}/search/dsl", params={"query": "hive_column where position >= 0 orderby name desc limit 3"}).json()
    assert [e["displayText"] for e in r["entities"]] == ["id", "id", "email"]
    assert client.get(f"{API}/search/dsl", params={"query": "hive_table where name = "}).status_code == 400


def test_saved_searches(client):
    s = {"name": "tables", "searchType": "BASIC", "searchParameters": {"typeName": "hive_table"}}
    r = client.post(f"{API}/search/saved", json=s)
    assert r.status_code == 200, r.text
    guid = r.json()["guid"]
    assert client.post(f"{API}/search/saved", json=s).status_code == 409
    assert [x["name"] for x in client.get(f"{API}/search/saved").json()] == ["tables"]
    create_sales_model(client)
    assert client.get(f"{API}/search/saved/execute/tables").json()["approximateCount"] == 2
    assert client.delete(f"{API}/search/saved/{guid}").status_code == 204


# ------------------------------------------------------------------ labels, business metadata, audits, relationships
def test_labels_custom_attributes_business_metadata(client):
    ga = create_sales_model(client)
    g = ga["-10"]
    assert client.post(f"{API}/entity/guid/{g}/labels", json=["gold", "finance"]).status_code == 204
    assert client.put(f"{API}/entity/guid/{g}/labels", json=["pii"]).status_code == 204
    assert client.request("DELETE", f"{API}/entity/guid/{g}/labels", json=["finance"]).status_code == 204
    assert client.get(f"{API}/entity/guid/{g}").json()["entity"]["labels"] == ["gold", "pii"]
    assert client.post(f"{API}/entity/guid/{g}/labels", json=["bad label"]).status_code == 400
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_table", "entityFilters": {
        "attributeName": "__labels", "operator": "eq", "attributeValue": "gold"}}).json()
    assert [e["guid"] for e in r["entities"]] == [g]

    client.post(f"{API}/types/typedefs", json={"businessMetadataDefs": [{"name": "Finance", "attributeDefs": [
        {"name": "costCenter", "typeName": "string", "options": {"applicableEntityTypes": '["DataSet"]', "maxStrLength": "20"}},
        {"name": "budget", "typeName": "double", "options": {"applicableEntityTypes": '["DataSet"]'}}]}]})
    r = client.post(f"{API}/entity/guid/{g}/businessmetadata", json={"Finance": {"costCenter": "CC-1", "budget": 12.5}})
    assert r.status_code == 204, r.text
    assert client.post(f"{API}/entity/guid/{ga['-30']}/businessmetadata",
                       json={"Finance": {"costCenter": "x"}}).status_code == 400
    ent = client.get(f"{API}/entity/guid/{g}").json()["entity"]
    assert ent["businessAttributes"] == {"Finance": {"costCenter": "CC-1", "budget": 12.5}}
    r = client.post(f"{API}/search/basic", json={"typeName": "hive_table", "entityFilters": {
        "attributeName": "Finance.budget", "operator": ">", "attributeValue": 10}}).json()
    assert [e["guid"] for e in r["entities"]] == [g]
    audits = client.get(f"{API}/entity/{g}/audit").json()
    actions = [a["action"] for a in audits]
    assert "ENTITY_CREATE" in actions and "LABEL_ADD" in actions and "BUSINESS_ATTRIBUTE_UPDATE" in actions


def test_relationship_api(client):
    ga = create_sales_model(client)
    r = client.get(f"{API}/entity/guid/{ga['-10']}").json()["entity"]
    rel_guid = r["relationshipAttributes"]["db"]["relationshipGuid"]
    rel = client.get(f"{API}/relationship/guid/{rel_guid}", params={"extendedInfo": "true"}).json()
    assert rel["relationship"]["typeName"] == "hive_table_db"
    assert set(rel["referredEntities"]) == {ga["-10"], ga["-1"]}
    # move table to a new db via the relationship API
    db2 = client.post(f"{API}/entity", json={"entity": hive_db("hr")}).json()["mutatedEntities"]["CREATE"][0]["guid"]
    r = client.post(f"{API}/relationship", json={"typeName": "hive_table_db", "end1": {"guid": ga["-10"]},
                                                  "end2": {"guid": db2}})
    assert r.status_code == 200, r.text
    ent = client.get(f"{API}/entity/guid/{ga['-10']}").json()["entity"]
    assert ent["relationshipAttributes"]["db"]["guid"] == db2  # SINGLE end: old relationship replaced
    new_rel = r.json()["guid"]
    assert client.delete(f"{API}/relationship/guid/{new_rel}").status_code == 204
    assert client.get(f"{API}/relationship/guid/{new_rel}").json()["relationship"]["status"] == "DELETED"


def test_unique_attribute_conflict_in_same_batch_is_merged(client):
    db = hive_db()
    db2 = hive_db(guid="-2")
    r = client.post(f"{API}/entity/bulk", json={"entities": [db, db2]}).json()
    assert len(r["mutatedEntities"]["CREATE"]) == 1
    assert r["guidAssignments"]["-1"] == r["guidAssignments"]["-2"]


def test_admin_endpoints_and_metrics(client):
    create_sales_model(client)
    assert client.get("/api/atlas/admin/version").json()["Name"] == "apache-atlas"
    s = client.get("/api/atlas/admin/session").json()
    assert s["userName"] == "admin"
    m = client.get("/api/atlas/admin/metrics").json()["data"]
    assert m["entity"]["entityActive"]["hive_table"] == 2
    assert m["entity"]["entityActive-typeAndSubTypes"]["DataSet"] >= 6


def test_auth(anon_client):
    assert anon_client.get(f"{API}/types/typedefs/headers").status_code == 401
    r = anon_client.get("/index.html", follow_redirects=False)
    assert r.status_code == 302 and r.headers["location"].endswith("login.jsp")
    assert anon_client.get("/login.jsp").status_code == 200
    r = anon_client.post("/j_spring_security_check", data={"j_username": "admin", "j_password": "wrong"})
    assert r.status_code == 401
    r = anon_client.post("/j_spring_security_check", data={"j_username": "admin", "j_password": "admin"})
    assert r.status_code == 200
    assert anon_client.get(f"{API}/types/typedefs/headers").status_code == 200  # session cookie
    assert anon_client.get("/index.html").status_code == 200


def test_hook_style_payload(client):
    """Payload shaped like the Hive hook: references by unique attributes, legacy 'attributes' refs, referredEntities."""
    client.post(f"{API}/entity", json={"entity": hive_db()})
    table = {"typeName": "hive_table", "guid": "-100",
             "attributes": {"qualifiedName": "sales.orders@cl1", "name": "orders",
                            "db": {"typeName": "hive_db", "uniqueAttributes": {"qualifiedName": "sales@cl1"}},
                            "columns": [{"guid": "-101", "typeName": "hive_column"}],
                            "sd": {"guid": "-102", "typeName": "hive_storagedesc"}}}
    referred = {
        "-101": {"typeName": "hive_column", "attributes": {
            "qualifiedName": "sales.orders.id@cl1", "name": "id", "type": "int",
            "table": {"typeName": "hive_table", "uniqueAttributes": {"qualifiedName": "sales.orders@cl1"}}}},
        "-102": {"typeName": "hive_storagedesc", "attributes": {
            "qualifiedName": "sales.orders@cl1_storage", "location": "hdfs://x/orders", "compressed": False,
            "table": {"guid": "-100", "typeName": "hive_table"}}},
    }
    r = client.post(f"{API}/entity", json={"entity": table, "referredEntities": referred})
    assert r.status_code == 200, r.text
    assert len(r.json()["mutatedEntities"]["CREATE"]) == 3
    t = qn(client, "hive_table", "sales.orders@cl1")
    assert t["relationshipAttributes"]["db"]["displayText"] == "sales"
    assert [c["displayText"] for c in t["relationshipAttributes"]["columns"]] == ["id"]
    assert t["relationshipAttributes"]["sd"]["typeName"] == "hive_storagedesc"
    # re-sending the same payload changes nothing and creates no duplicates
    r = client.post(f"{API}/entity", json={"entity": table, "referredEntities": referred}).json()
    assert "CREATE" not in r.get("mutatedEntities", {})
    t = qn(client, "hive_table", "sales.orders@cl1")
    assert len(t["relationshipAttributes"]["columns"]) == 1


def test_trailing_slash_like_jersey(client):
    # the official apache-atlas Python client calls e.g. /api/atlas/v2/types/typedefs/
    assert client.get(f"{API}/types/typedefs/").status_code == 200
    assert client.get(f"{API}/types/typedefs/headers/").status_code == 200
