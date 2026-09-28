def hive_db(name="sales", cluster="cl1", guid="-1"):
    return {"typeName": "hive_db", "guid": guid,
            "attributes": {"qualifiedName": f"{name}@{cluster}", "name": name, "clusterName": cluster,
                           "description": f"{name} database"}}


def hive_table(db_ref, name, cols, guid, db="sales", cluster="cl1", extra=None):
    qn = f"{db}.{name}@{cluster}"
    table = {"typeName": "hive_table", "guid": guid,
             "attributes": {"qualifiedName": qn, "name": name, "owner": "etl", "createTime": 1700000000000,
                            **(extra or {})},
             "relationshipAttributes": {"db": db_ref,
                                        "columns": [{"guid": f"{guid}-c{i}"} for i in range(len(cols))]}}
    columns = []
    for i, (cname, ctype) in enumerate(cols):
        columns.append({"typeName": "hive_column", "guid": f"{guid}-c{i}",
                        "attributes": {"qualifiedName": f"{db}.{name}.{cname}@{cluster}", "name": cname,
                                       "type": ctype, "position": i},
                        "relationshipAttributes": {"table": {"guid": guid}}})
    return table, columns


def create_sales_model(client):
    """sales db, 2 tables with columns and a process customers -> customer_summary."""
    db = hive_db()
    t1, c1 = hive_table({"guid": "-1"}, "customers", [("id", "int"), ("email", "string")], "-10")
    t2, c2 = hive_table({"guid": "-1"}, "customer_summary", [("id", "int"), ("cnt", "bigint")], "-20")
    ents = [db, t1, t2] + c1 + c2
    r = client.post("/api/atlas/v2/entity/bulk", json={"entities": ents})
    assert r.status_code == 200, r.text
    ga = r.json()["guidAssignments"]
    proc = {"typeName": "hive_process", "guid": "-30",
            "attributes": {"qualifiedName": "sales.summary_job@cl1", "name": "summary_job",
                           "operationType": "CREATETABLE_AS_SELECT", "queryText": "insert ...", "queryPlan": "",
                           "queryId": "q1", "startTime": 1700000000000, "endTime": 1700000001000,
                           "userName": "etl", "clusterName": "cl1"},
            "relationshipAttributes": {
                "inputs": [{"typeName": "hive_table", "uniqueAttributes": {"qualifiedName": "sales.customers@cl1"}}],
                "outputs": [{"guid": ga["-20"]}]}}
    r = client.post("/api/atlas/v2/entity", json={"entity": proc})
    assert r.status_code == 200, r.text
    ga.update(r.json()["guidAssignments"])
    return ga
