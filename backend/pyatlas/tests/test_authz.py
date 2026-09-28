"""Authorization (Atlas simple authorizer) tests."""
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from pyatlas.authz import SimpleAuthorizer, is_match
from tests.conftest import _fresh_client
from tests.helpers import create_sales_model

V2 = "/api/atlas/v2"
A = "/api/atlas/admin"
DENIED = "ATLAS-403-00-001"


def _users_file(users):
    d = Path(tempfile.mkdtemp(prefix="pyatlas-users-"))
    p = d / "users-credentials.properties"
    p.write_text("\n".join(f"{u}={g}::{hashlib.sha256(u.encode()).hexdigest()}" for u, g in users.items()) + "\n",
                 encoding="utf-8")
    return p


def _policy_file(policy):
    p = Path(tempfile.mkdtemp(prefix="pyatlas-policy-")) / "policy.json"
    p.write_text(json.dumps(policy), encoding="utf-8")
    return p


def _as(client, user):
    client.auth = (user, user) if user != "admin" else ("admin", "admin")
    return client


def _denied(r, user=None, what=None):
    assert r.status_code == 403, (r.status_code, r.text)
    body = r.json()
    assert body["errorCode"] == DENIED
    if user:
        assert body["errorMessage"].startswith(f"{user} is not authorized to perform")
    if what:
        assert what in body["errorMessage"], body["errorMessage"]


# ------------------------------------------------------------------ matching semantics
def test_pattern_matching_is_atlas_compatible():
    assert is_match("hive_table", [".*"])
    assert is_match("hive_table", ["HIVE_TABLE"])           # case-insensitive equality
    assert is_match("hive_table", ["hive_.*"])              # full regex match
    assert not is_match("my_hive_table", ["hive_.*"])       # String.matches() = whole value
    assert is_match(None, [])                               # absent value always matches
    assert not is_match("x", [])
    az = SimpleAuthorizer({"roles": {"R": {"typePermissions": [{"privileges": ["type-create"],
                                                               "typeCategories": [".*"], "typeNames": [".*"]}]}},
                           "userRoles": {"u": ["R"]}, "groupRoles": {"G": ["R"]}})
    assert az.roles("u", []) == {"R"} and az.roles("x", ["G"]) == {"R"}
    # type-read is implied by type-create/update/delete
    assert az.type("u", set(), "type-read", "ENTITY", "hive_table")
    assert not az.type("u", set(), "type-delete", "ENTITY", "hive_table")


# ------------------------------------------------------------------ default policy (conf/atlas-simple-authz-policy.json)
@pytest.fixture
def roles_client():
    users = {"admin": "ADMIN", "steward": "DATA_STEWARD", "scientist": "RANGER_TAG_SYNC", "guest": "GUEST"}
    c = _fresh_client(users_file=_users_file(users))  # password = user name
    yield c
    c.__exit__(None, None, None)


def test_default_policy_roles(roles_client):
    c = roles_client
    _as(c, "admin")
    c.post(f"{V2}/types/typedefs", json={
        "classificationDefs": [{"name": "Sensitive"}],
        "businessMetadataDefs": [{"name": "Ops", "attributeDefs": [
            {"name": "team", "typeName": "string",
             "options": {"applicableEntityTypes": '["DataSet"]', "maxStrLength": "50"}}]}]})
    ga = create_sales_model(c)
    table = ga["-10"]

    # --- session flags drive the UI's create/edit buttons
    assert _as(c, "admin").get(f"{A}/session").json()["atlas.entity.create.allowed"] is True
    s = _as(c, "scientist").get(f"{A}/session").json()
    assert s["atlas.entity.create.allowed"] is False and s["atlas.entity.update.allowed"] is False
    assert s["groups"] == ["RANGER_TAG_SYNC"]
    assert _as(c, "steward").get(f"{A}/session").json()["atlas.entity.update.allowed"] is True

    # --- DATA_SCIENTIST: read only
    _as(c, "scientist")
    assert c.get(f"{V2}/entity/guid/{table}").status_code == 200
    assert c.get(f"{V2}/lineage/{ga['-20']}").status_code == 200
    assert len(c.get(f"{V2}/types/typedefs").json()["entityDefs"]) > 10
    _denied(c.post(f"{V2}/entity", json={"entity": {"typeName": "hive_db", "attributes": {
        "qualifiedName": "x@cl1", "name": "x", "clusterName": "cl1"}}}), "scientist", "create entity: type=hive_db")
    _denied(c.post(f"{V2}/entity/guid/{table}/classifications", json=[{"typeName": "Sensitive"}]), "scientist",
            "add classification")
    _denied(c.put(f"{V2}/entity/guid/{table}/labels", json=["l1"]), "scientist", "add label")
    _denied(c.delete(f"{V2}/entity/guid/{table}"), "scientist", "delete entity")
    _denied(c.post(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "X"}]}), "scientist",
            "create classification-def X")
    _denied(c.post(f"{A}/audits", json={}), "scientist", "Admin Audits")
    _denied(c.post(f"{A}/export", json={"itemsToExport": [{"guid": table}]}), "scientist", "export")
    _denied(c.put(f"{A}/purge", json=[table]), "scientist", "purge")
    _denied(c.get(f"{A}/debug/metrics"))
    _denied(c.get(f"{A}/patches"))

    # --- DATA_STEWARD: entity + relationship CRUD without delete, no type/admin changes
    _as(c, "steward")
    r = c.post(f"{V2}/entity", json={"entity": {"typeName": "hive_db", "attributes": {
        "qualifiedName": "hr@cl1", "name": "hr", "clusterName": "cl1"}}})
    assert r.status_code == 200, r.text
    hr = r.json()["mutatedEntities"]["CREATE"][0]["guid"]
    assert c.post(f"{V2}/entity/guid/{table}/classifications", json=[{"typeName": "Sensitive"}]).status_code == 204
    assert c.put(f"{V2}/entity/guid/{table}/labels", json=["gold"]).status_code == 204
    assert c.post(f"{V2}/entity/guid/{table}/businessmetadata", json={"Ops": {"team": "crm"}}).status_code == 204
    assert c.put(f"{V2}/entity/guid/{hr}", params={"name": "description"}, json="HR").status_code == 200
    _denied(c.delete(f"{V2}/entity/guid/{hr}"), "steward", f"delete entity: guid={hr}")
    _denied(c.put(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "Sensitive", "description": "x"}]}),
            "steward", "update classification-def Sensitive")
    _denied(c.delete(f"{V2}/types/typedef/name/Sensitive"), "steward", "delete classification-def Sensitive")
    _denied(c.post(f"{A}/import", files={"data": ("e.zip", b"PK", "application/zip")}), "steward", "importData")

    # --- a user without any role sees nothing
    _as(c, "guest")
    _denied(c.get(f"{V2}/entity/guid/{table}"), "guest", f"read entity: guid={table}")
    _denied(c.get(f"{V2}/entity/guid/{table}/classifications"))
    _denied(c.get(f"{V2}/lineage/{table}"), "guest", "read entity lineage")
    _denied(c.get(f"{V2}/types/typedef/name/hive_table"), "guest", "read type hive_table")
    assert c.get(f"{V2}/types/typedefs").json()["entityDefs"] == []
    assert c.get(f"{V2}/types/typedefs/headers").json() == []
    res = c.post(f"{V2}/search/basic", json={"typeName": "hive_table"}).json()
    assert res["entities"] and all(e["guid"] == "-1" and e["attributes"] == {} and e["classificationNames"] == []
                                   for e in res["entities"])
    assert {e["typeName"] for e in res["entities"]} == {"hive_table"}
    q = c.get(f"{V2}/search/quick", params={"query": "customers"}).json()
    assert all(e["guid"] == "-1" for e in q["searchResults"]["entities"])
    dsl = c.get(f"{V2}/search/dsl", params={"query": "hive_db"}).json()
    assert all(e["guid"] == "-1" for e in dsl["entities"])

    # --- admin still can do everything, and deletes what the steward could not
    _as(c, "admin")
    assert c.delete(f"{V2}/entity/guid/{hr}").status_code == 200
    assert c.post(f"{A}/audits", json={}).status_code == 200
    assert c.get(f"{V2}/entity/guid/{table}").json()["entity"]["labels"] == ["gold"]


# ------------------------------------------------------------------ fine grained custom policy
CUSTOM_POLICY = {
    "roles": {
        "ROLE_ADMIN": {
            "adminPermissions": [{"privileges": [".*"]}],
            "typePermissions": [{"privileges": [".*"], "typeCategories": [".*"], "typeNames": [".*"]}],
            "entityPermissions": [{"privileges": [".*"], "entityTypes": [".*"], "entityIds": [".*"],
                                   "entityClassifications": [".*"], "labels": [".*"], "businessMetadata": [".*"],
                                   "attributes": [".*"], "classifications": [".*"]}],
            "relationshipPermissions": [{"privileges": [".*"], "relationshipTypes": [".*"],
                                         "end1EntityType": [".*"], "end1EntityId": [".*"],
                                         "end1EntityClassification": [".*"], "end2EntityType": [".*"],
                                         "end2EntityId": [".*"], "end2EntityClassification": [".*"]}]},
        "TABLE_CURATOR": {
            "typePermissions": [{"privileges": ["type-read"], "typeCategories": [".*"], "typeNames": [".*"]}],
            "entityPermissions": [
                # DataSet covers hive_table and hive_column through their super types; only untagged or
                # "Public" entities
                {"privileges": ["entity-read", "entity-update", "entity-add-label", "entity-add-classification",
                                "entity-update-business-metadata"],
                 "entityTypes": ["DataSet"], "entityIds": ["sales\\..*@cl1"], "entityClassifications": ["Public"],
                 "labels": ["ok_.*"], "businessMetadata": ["Ops"], "attributes": [".*"],
                 "classifications": ["Public.*"]}],
            "relationshipPermissions": [{"privileges": ["add-relationship"], "relationshipTypes": ["hive_table_db"],
                                         "end1EntityType": [".*"], "end1EntityId": [".*"],
                                         "end1EntityClassification": [".*"], "end2EntityType": ["hive_db"],
                                         "end2EntityId": ["sales@cl1"], "end2EntityClassification": [".*"]}]},
    },
    "userRoles": {"admin": ["ROLE_ADMIN"]},
    "groupRoles": {"CURATORS": ["TABLE_CURATOR"]},
}


def test_custom_policy_patterns():
    c = _fresh_client(users_file=_users_file({"admin": "ADMIN", "cur": "CURATORS"}),
                      authz_policy_file=_policy_file(CUSTOM_POLICY))
    try:
        _as(c, "admin")
        c.post(f"{V2}/types/typedefs", json={
            "classificationDefs": [{"name": "Sensitive"}, {"name": "Public"}, {"name": "PublicSub", "superTypes": ["Public"]}],
            "businessMetadataDefs": [
                {"name": n, "attributeDefs": [{"name": "team", "typeName": "string", "options": {
                    "applicableEntityTypes": '["DataSet"]', "maxStrLength": "50"}}]} for n in ("Ops", "Finance")]})
        ga = create_sales_model(c)
        table, summary, col = ga["-10"], ga["-20"], ga["-10-c0"]

        _as(c, "cur")
        # entity type restriction (hive_db is no DataSet) and entity id restriction (qualifiedName pattern)
        assert c.get(f"{V2}/entity/guid/{table}").status_code == 200
        assert c.get(f"{V2}/entity/guid/{col}").status_code == 200
        _denied(c.get(f"{V2}/entity/guid/{ga['-1']}"), "cur")
        _denied(c.get(f"{V2}/entity/guid/{ga['-30']}"), "cur")      # hive_process is no DataSet
        # labels / business metadata / classification name patterns
        assert c.put(f"{V2}/entity/guid/{table}/labels", json=["ok_1"]).status_code == 204
        _denied(c.put(f"{V2}/entity/guid/{table}/labels", json=["secret"]), "cur", "add label: guid=")
        assert c.post(f"{V2}/entity/guid/{table}/businessmetadata", json={"Ops": {"team": "a"}}).status_code == 204
        _denied(c.post(f"{V2}/entity/guid/{table}/businessmetadata", json={"Finance": {"team": "a"}}), "cur",
                "business-metadata-name=Finance")
        _denied(c.post(f"{V2}/entity/guid/{col}/classifications", json=[{"typeName": "Sensitive"}]), "cur",
                "classification=Sensitive")
        assert c.post(f"{V2}/entity/guid/{col}/classifications", json=[{"typeName": "PublicSub"}]).status_code == 204
        # a tagged entity stays readable when every tag (or one of its super types) is allowed:
        # "PublicSub" is covered by entityClassifications ["Public"] through its super type
        assert c.get(f"{V2}/entity/guid/{col}").status_code == 200
        # relationship: end types / ids
        r = c.post(f"{V2}/relationship", json={"typeName": "hive_table_db", "end1": {"guid": summary},
                                               "end2": {"guid": ga["-1"]}})
        assert r.status_code in (200, 409), r.text   # permission granted (409 = already exists)
        _as(c, "admin")
        other = c.post(f"{V2}/entity", json={"entity": {"typeName": "hive_db", "attributes": {
            "qualifiedName": "hr@cl1", "name": "hr", "clusterName": "cl1"}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
        _as(c, "cur")
        _denied(c.post(f"{V2}/relationship", json={"typeName": "hive_table_db", "end1": {"guid": summary},
                                                   "end2": {"guid": other}}), "cur", "add-relationship")

        # tagging the table with Sensitive hides it and - through propagation along lineage - the summary table
        _as(c, "admin")
        assert c.post(f"{V2}/entity/guid/{table}/classifications", json=[{"typeName": "Sensitive"}]).status_code == 204
        _as(c, "cur")
        _denied(c.get(f"{V2}/entity/guid/{table}"), "cur")
        _denied(c.get(f"{V2}/entity/guid/{summary}"), "cur")   # propagated Sensitive
        res = c.post(f"{V2}/search/basic", json={"typeName": "hive_table"}).json()
        assert sorted(e["guid"] for e in res["entities"]) == ["-1", "-1"]
        lin = c.get(f"{V2}/lineage/{col}")
        assert lin.status_code in (200, 404)
        # the curator may not update the entity any more either
        _denied(c.put(f"{V2}/entity/guid/{table}", params={"name": "description"}, json="x"), "cur")
        # bulk/headers only lists readable entities
        hdrs = c.get(f"{V2}/entity/bulk/headers", params={"tagUpdateStartTime": 0}).json()["guidHeaderMap"]
        assert table not in hdrs and col in hdrs
    finally:
        c.__exit__(None, None, None)


def test_none_authorizer_allows_everything():
    c = _fresh_client(users_file=_users_file({"admin": "ADMIN", "guest": "GUEST"}), authorizer="none")
    try:
        _as(c, "admin")
        ga = create_sales_model(c)
        _as(c, "guest")
        assert c.get(f"{V2}/entity/guid/{ga['-10']}").status_code == 200
        assert c.post(f"{A}/audits", json={}).status_code == 200
        assert c.get(f"{A}/session").json()["atlas.entity.create.allowed"] is True
    finally:
        c.__exit__(None, None, None)
