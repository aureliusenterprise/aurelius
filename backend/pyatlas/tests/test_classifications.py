"""Classification management of the frontend (administrators): list with use, create, change, delete."""
import pytest

from pyatlas.oidc import JwksCache
from tests.conftest import _fresh_client
from tests.test_oidc import ISS, JWK, bearer, token

A = "/api/aurelius/classifications"
V2 = "/api/atlas/v2"


@pytest.fixture()
def c(monkeypatch):
    monkeypatch.setattr(JwksCache, "_http_fetch", lambda self: {"keys": [JWK]})
    client = _fresh_client(oidc_enabled=True, oidc_issuers=ISS)
    client.auth = None
    client.admin = bearer(token("anna", ("ROLE_ADMIN",)))
    client.steward = bearer(token("stella", ("DATA_STEWARD",)))
    try:
        yield client
    finally:
        client.__exit__(None, None, None)


def _entity(c, name, classifications=()):
    body = {"entity": {"typeName": "m4i_data_entity", "attributes": {"qualifiedName": name, "name": name},
                       "classifications": [{"typeName": t} for t in classifications]}}
    r = c.post(f"{V2}/entity", json=body, headers=c.admin)
    assert r.status_code == 200, r.text
    return r.json()["mutatedEntities"]["CREATE"][0]["guid"]


def test_the_model_classifications_have_display_names(c):
    rows = {r["name"]: r for r in c.get(A, headers=c.steward).json()}
    assert {"PII", "key_data", "low_risk", "medium_risk", "high_risk"} <= set(rows)
    pii = rows["PII"]
    assert pii["displayName"] == "Has PII" and pii["displayNames"] == {"nl-NL": "Bevat PII"}
    assert pii["description"].startswith("Personally identifiable")
    assert "m4i_data_attribute" in pii["entityTypes"] and pii["usage"] == {"direct": 0, "propagated": 0}


def test_create_change_and_delete(c):
    body = {"name": "confidential", "displayName": "Confidential", "displayNames": {"nl-NL": "Vertrouwelijk"},
            "description": "Only for internal use", "entityTypes": ["m4i_data_entity", "m4i_dataset"]}
    r = c.post(A, json=body, headers=c.admin)
    assert r.status_code == 200, r.text
    assert r.json()["displayName"] == "Confidential"
    # a classification type for Atlas as well: usable on entities right away
    td = c.get(f"{V2}/types/classificationdef/name/confidential", headers=c.admin).json()
    assert td["options"] == {"displayName": "Confidential", "displayName.nl-NL": "Vertrouwelijk"}
    assert td["entityTypes"] == ["m4i_data_entity", "m4i_dataset"] and td["createdBy"] == "anna"
    # change: display names, description and allowed types (the name is fixed)
    r = c.put(f"{A}/confidential", json={**body, "displayName": "Internal", "entityTypes": ["m4i_data_entity"]},
              headers=c.admin)
    assert r.status_code == 200, r.text
    assert r.json()["displayName"] == "Internal" and r.json()["entityTypes"] == ["m4i_data_entity"]
    r = c.put(f"{A}/confidential", json={**body, "name": "secret"}, headers=c.admin)
    assert r.status_code == 400 and r.json()["field"] == "name"
    # in use: no delete; counts direct and propagated use
    guid = _entity(c, "E1", ["confidential"])
    row = next(r for r in c.get(A, headers=c.admin).json() if r["name"] == "confidential")
    assert row["usage"]["direct"] == 1
    r = c.delete(f"{A}/confidential", headers=c.admin)
    assert r.status_code == 409 and "still attached to 1" in r.json()["errorMessage"]
    assert c.delete(f"{V2}/entity/guid/{guid}/classification/confidential", headers=c.admin).status_code == 204
    assert c.delete(f"{A}/confidential", headers=c.admin).status_code == 204
    assert c.get(f"{V2}/types/classificationdef/name/confidential", headers=c.admin).status_code == 404


def test_names_are_unique(c):
    ok = {"name": "secret", "displayName": "Secret", "entityTypes": ["m4i_data_entity"]}
    assert c.post(A, json=ok, headers=c.admin).status_code == 200
    # the technical name: unique among all types, ignoring case
    for name in ("secret", "SECRET", "PII", "m4i_data_entity", "pii"):
        r = c.post(A, json={**ok, "name": name, "displayName": f"x {name}"}, headers=c.admin)
        assert r.status_code == 409 and r.json()["field"] == "name", name
    # display names: unique among the classifications, per language, ignoring case; a classification's
    # technical name counts as its display name
    for display, names in (("secret", {}), ("HAS pii", {}), ("x", {"nl-NL": "bevat pii"}), ("Pii", {})):
        r = c.post(A, json={**ok, "name": "other", "displayName": display, "displayNames": names},
                   headers=c.admin)
        assert r.status_code == 409, (display, r.text)
    # changing a classification keeps its own names
    assert c.put(f"{A}/secret", json={**ok, "description": "d"}, headers=c.admin).status_code == 200
    # invalid input
    for bad in ({**ok, "name": "1abc"}, {**ok, "name": "a b"}, {**ok, "name": "other", "displayName": ""},
                {**ok, "name": "other", "displayName": "O", "entityTypes": ["no_such_type"]}):
        assert c.post(A, json=bad, headers=c.admin).status_code == 400, bad


def test_only_administrators_change_classifications(c):
    body = {"name": "secret", "displayName": "Secret", "entityTypes": ["m4i_data_entity"]}
    assert c.post(A, json=body, headers=c.steward).status_code == 403
    assert c.put(f"{A}/PII", json={"displayName": "x", "entityTypes": []}, headers=c.steward).status_code == 403
    assert c.delete(f"{A}/low_risk", headers=c.steward).status_code == 403
    assert c.get(f"{V2}/types/classificationdef/name/low_risk", headers=c.admin).status_code == 200
    # everybody may read the list (the editors need the classifications)
    assert c.get(A, headers=c.steward).status_code == 200
    assert c.get(A).status_code == 401


def test_propagated_use_is_counted(c):
    # a data attribute's classification propagates to its data entity (m4i_data_entity_attribute_assignment)
    e = _entity(c, "E2")
    attr = {"entity": {"typeName": "m4i_data_attribute", "attributes": {"qualifiedName": "A1", "name": "A1"},
                       "relationshipAttributes": {"dataEntity": [{"guid": e, "typeName": "m4i_data_entity"}]},
                       "classifications": [{"typeName": "PII", "propagate": True}]}}
    assert c.post(f"{V2}/entity", json=attr, headers=c.admin).status_code == 200
    row = next(r for r in c.get(A, headers=c.admin).json() if r["name"] == "PII")
    assert row["usage"] == {"direct": 1, "propagated": 1}
    assert c.delete(f"{A}/PII", headers=c.admin).status_code == 409
