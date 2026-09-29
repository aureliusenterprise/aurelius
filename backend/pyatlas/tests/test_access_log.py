"""Access log (logins per day in Kibana) and the report fields of audit events."""
from pyatlas.oidc import JwksCache
from tests.conftest import _fresh_client
from tests.test_oidc import BROWSER, ISS, JWK, bearer, token

V2 = "/api/atlas/v2"


def access_docs(c):
    st = c.app.state.services.store

    async def dump():
        return [d async for _id, d in st.scan(st.access, {"match_all": {}}, sort_field="session")]
    return c.portal.call(dump)


def test_one_login_per_keycloak_session(monkeypatch):
    monkeypatch.setattr(JwksCache, "_http_fetch", lambda self: {"keys": [JWK]})
    c = _fresh_client(oidc_enabled=True, oidc_issuers=ISS)
    c.auth = None
    try:
        t1 = token("steward1", ("DATA_STEWARD",), sid="s-1")
        for _ in range(3):
            assert c.get(f"{V2}/types/typedefs/headers", headers={**bearer(t1), "X-Forwarded-For": "10.0.0.7, 10.0.0.1"}) \
                .status_code == 200
        c.get(f"{V2}/types/typedefs/headers", headers=bearer(token("steward1", ("DATA_STEWARD",), sid="s-2")))
        c.get(f"{V2}/types/typedefs/headers", headers=bearer(token("svc", ("ROLE_ADMIN",), azp="pipeline")))
        c.get(f"{V2}/types/typedefs/headers", headers=bearer(token("svc", ("ROLE_ADMIN",), azp="pipeline")))
        docs = access_docs(c)
        keycloak = [d for d in docs if d["method"] == "keycloak"]
        assert sorted(d["session"].split(":")[1] for d in keycloak if d["user"] == "steward1") == ["s-1", "s-2"]
        first = next(d for d in keycloak if d["session"] == "keycloak:s-1")
        # X-Forwarded-For is only believed from a trusted proxy (none configured here)
        assert first["ip"] == "testclient" and first["client"] == "m4i_atlas" and "DATA_STEWARD" in first["groups"]
        # a service account token without session: once per client, user and day
        assert len([d for d in keycloak if d["user"] == "svc"]) == 1
    finally:
        c.__exit__(None, None, None)


def test_form_and_basic_logins():
    c = _fresh_client()
    try:
        for _ in range(3):                          # a script with Basic auth: once per user and day
            c.get(f"{V2}/types/typedefs/headers")
        c.auth = None
        assert c.post("/j_spring_security_check", data={"j_username": "admin", "j_password": "admin"},
                      headers=BROWSER).status_code == 200
        methods = sorted(d["method"] for d in access_docs(c))
        assert methods.count("form") == 1 and methods.count("basic") == 1
    finally:
        c.__exit__(None, None, None)


def test_audit_events_name_the_entity():
    c = _fresh_client()
    try:
        g = c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_domain", "attributes": {
            "qualifiedName": "sales", "name": "Sales"}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
        c.put(f"{V2}/entity/guid/{g}", params={"name": "definition"}, json="All sales data")
        st = c.app.state.services.store

        async def dump():
            return [d async for _id, d in st.scan(st.audit, {"term": {"entityId": g}}, sort_field="eventKey")]
        events = c.portal.call(dump)
        assert [(e["action"], e["user"], e["typeName"], e["entityName"]) for e in events] == [
            ("ENTITY_CREATE", "admin", "m4i_data_domain", "Sales"), ("ENTITY_UPDATE", "admin", "m4i_data_domain", "Sales")]
        # the Atlas audit API answers as before
        api = c.get(f"{V2}/entity/{g}/audit").json()
        assert "typeName" not in api[0] and api[0]["user"] == "admin"
    finally:
        c.__exit__(None, None, None)


def test_client_address_behind_a_trusted_proxy():
    from types import SimpleNamespace
    from pyatlas.auth import AuthMiddleware

    def req(peer, fwd=None):
        return SimpleNamespace(client=SimpleNamespace(host=peer), headers={"x-forwarded-for": fwd} if fwd else {})
    mw = AuthMiddleware(lambda *a: None, [], trusted_proxies="172.16.0.0/12, 10.1.2.3")
    # the proxy appends the address it saw; what the client sent before is ignored
    assert mw.client_ip(req("172.18.0.5", "6.6.6.6, 203.0.113.9")) == "203.0.113.9"
    assert mw.client_ip(req("10.1.2.3", "203.0.113.9")) == "203.0.113.9"
    assert mw.client_ip(req("198.51.100.1", "6.6.6.6")) == "198.51.100.1"        # not a trusted proxy
    assert mw.client_ip(req("172.18.0.5")) == "172.18.0.5"
