from tests.helpers import create_sales_model

DSL = "/api/atlas/v2/search/dsl"


def names(r):
    return [e["displayText"] for e in r.get("entities", [])]


def q(client, query, **kw):
    r = client.get(DSL, params={"query": query, **kw})
    assert r.status_code == 200, r.text
    return r.json()


def test_dsl_queries(client):
    client.post("/api/atlas/v2/types/typedefs", json={"classificationDefs": [
        {"name": "Sensitive", "attributeDefs": [{"name": "level", "typeName": "int"}]}]})
    ga = create_sales_model(client)
    client.post(f"/api/atlas/v2/entity/guid/{ga['-10-c1']}/classifications", json=[{"typeName": "Sensitive", "attributes": {"level": 3}}])

    assert names(q(client, "hive_table")) == ["customer_summary", "customers"]
    assert names(q(client, "from hive_table where name = 'customers'")) == ["customers"]
    assert names(q(client, "hive_table where name = \"customers\" or name = 'customer_summary' orderby name desc")) == \
        ["customers", "customer_summary"]
    assert names(q(client, "hive_column where position > 0 and name like 'e*'")) == ["email"]
    assert names(q(client, "hive_column where (name = 'id' or name = 'cnt') and position = 0")) == ["id", "id"]
    assert names(q(client, "hive_column where name in ['id', 'email'] orderby name limit 2")) == ["email", "id"]
    assert names(q(client, "hive_column where name in ['id', 'email'] orderby name limit 2 offset 1")) == ["id", "id"]
    # reference traversal and aliases
    assert names(q(client, "hive_column where table.name = 'customers' orderby name")) == ["email", "id"]
    assert names(q(client, "hive_table as t where t.name = 'customers'")) == ["customers"]
    assert names(q(client, "hive_table where db.name = 'sales' and name = 'customers'")) == ["customers"]
    # navigation
    assert names(q(client, "hive_table where name = 'customers' columns orderby name")) == ["email", "id"]
    assert names(q(client, "hive_db where name = 'sales' tables orderby name")) == ["customer_summary", "customers"]
    # classifications
    assert names(q(client, "hive_column isa Sensitive")) == ["email"]
    assert names(q(client, "hive_column is Sensitive")) == ["email"]
    assert names(q(client, "Sensitive")) == ["email"]
    assert names(q(client, "Sensitive where level > 2")) == ["email"]
    assert names(q(client, "hive_column where Sensitive.level = 3")) == ["email"]
    assert q(client, "Sensitive where level > 5").get("entities") is None
    assert names(q(client, "hive_table isa _NOT_CLASSIFIED orderby name")) == ["customer_summary", "customers"]
    # has / system attributes
    assert len(q(client, "hive_column has position")["entities"]) == 4
    assert names(q(client, "hive_table where __guid = '%s'" % ga["-10"])) == ["customers"]
    assert len(q(client, "hive_table has db")["entities"]) == 2
    # typeName / classification parameters (DiscoveryREST semantics)
    assert names(q(client, "where name = 'customers'", typeName="hive_table")) == ["customers"]
    assert names(q(client, "", typeName="hive_column", classification="Sensitive")) == ["email"]


def test_dsl_select_groupby_aggregates(client):
    create_sales_model(client)
    r = q(client, "hive_column select name, position orderby name")
    assert r["attributes"]["name"] == ["name", "position"]
    assert r["attributes"]["values"] == [["cnt", 1], ["email", 1], ["id", 0]]   # duplicate rows are collapsed
    r = q(client, "hive_column select count() as c, max(position), min(name)")
    assert r["attributes"] == {"name": ["c", "max(position)", "min(name)"], "values": [[4, 1, "cnt"]]}
    r = q(client, "hive_column groupby(type) select type, count() orderby type")
    assert r["attributes"]["values"] == [["bigint", 1], ["int", 2], ["string", 1]]
    r = q(client, "hive_column where table.name = 'customers' select name, table.name orderby name")
    assert r["attributes"]["values"] == [["email", "customers"], ["id", "customers"]]
    r = q(client, "hive_column select sum(position)")
    assert r["attributes"]["values"] == [[2.0]]


def test_dsl_errors(client):
    for bad in ["nosuchtype", "hive_table where", "hive_table where foo = 1", "hive_table where name = 'x' ) ",
                "hive_table orderby", "hive_table limit x"]:
        r = client.get(DSL, params={"query": bad})
        assert r.status_code == 400, (bad, r.text)
        assert r.json()["errorCode"] == "ATLAS-400-00-059"
