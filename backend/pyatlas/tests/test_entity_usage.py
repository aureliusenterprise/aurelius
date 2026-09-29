"""Data entity "uses" data entity (m4i_data_entity_usage): many to many, both directions visible."""
V2 = "/api/atlas/v2"


def entity(client, qn, **rel):
    body = {"entity": {"typeName": "m4i_data_entity", "attributes": {"qualifiedName": qn, "name": qn},
                       "relationshipAttributes": rel}}
    r = client.post(f"{V2}/entity", json=body)
    assert r.status_code == 200, r.text
    m = r.json()["mutatedEntities"]
    return (m.get("CREATE") or m.get("UPDATE"))[0]["guid"]


def rel(client, guid, name):
    e = client.get(f"{V2}/entity/guid/{guid}").json()["entity"]
    return sorted(x["guid"] for x in e["relationshipAttributes"].get(name) or []
                  if x.get("relationshipStatus", "ACTIVE") == "ACTIVE")


def test_uses_relationship_is_many_to_many(client):
    rd = client.get(f"{V2}/types/relationshipdef/name/m4i_data_entity_usage").json()
    assert (rd["endDef1"]["name"], rd["endDef2"]["name"]) == ("uses", "usedBy")
    assert rd["endDef1"]["cardinality"] == rd["endDef2"]["cardinality"] == "SET"
    a, b, c = (entity(client, q) for q in ("a", "b", "c"))
    # a uses b and c; c uses b
    entity(client, "a", uses=[{"guid": b, "typeName": "m4i_data_entity"}, {"guid": c, "typeName": "m4i_data_entity"}])
    entity(client, "c", uses=[{"guid": b, "typeName": "m4i_data_entity"}])
    assert rel(client, a, "uses") == sorted([b, c])
    assert rel(client, b, "usedBy") == sorted([a, c])
    assert rel(client, c, "usedBy") == [a] and rel(client, c, "uses") == [b]
    # set from the other side: b is used by c only
    entity(client, "b", usedBy=[{"guid": c, "typeName": "m4i_data_entity"}])
    assert rel(client, b, "usedBy") == [c]
    assert rel(client, a, "uses") == [c]
    # the parent/child hierarchy is independent
    assert rel(client, a, "parentEntity") == [] and rel(client, b, "childEntity") == []
