"""Multi-tenancy: tenants share one pyatlas, but not their data, realm, sessions, logs or jobs."""
import json
import logging
import tempfile
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from pyatlas.config import Settings
from pyatlas.logctx import JsonFormatter, TenantFilter, tenant_var
from pyatlas.main import create_app
from pyatlas.oidc import JwksCache, KeycloakPasswordAuthenticator
from pyatlas.tenancy import check_tenant_id, valid_tenant_id
from tests.fake_es import FakeElasticsearch
from tests.test_oidc import BROWSER, _key

V2 = "/api/atlas/v2"
PROXY = ("10.0.0.5", 40000)          # the reverse proxy (trusted)
ISS = "http://localhost:8080/aurelius/auth/realms/{tenant}"
KEYS = {t: _key(f"{t}-k1") for t in ("m4i", "acme", "beta")}   # every realm signs with its own key


def realm_token(realm, user="steward1", roles=("DATA_STEWARD",), iss=None, **claims):
    now = int(time.time())
    body = {"iss": iss or ISS.format(tenant=realm), "sub": "f:1", "typ": "Bearer", "azp": "m4i_atlas",
            "iat": now, "exp": now + 300, "preferred_username": user,
            "realm_access": {"roles": list(roles)}, "sid": f"{realm}-{user}"}
    body.update(claims)
    key, jwk = KEYS[realm]
    return jwt.encode(body, key, algorithm="RS256", headers={"kid": jwk["kid"]})


def h(tenant, token=None, **extra):
    out = {"X-Aurelius-Tenant": tenant, **BROWSER, **extra}
    if token:
        out["Authorization"] = f"Bearer {token}"
    return out


def _fetch(self):
    realm = self.url.split("/realms/")[1].split("/")[0]
    return {"keys": [KEYS[realm][1]]} if realm in KEYS else {"keys": []}


def mt_app(monkeypatch, fake=None, **overrides):
    monkeypatch.setattr(JwksCache, "_http_fetch", _fetch)
    kw = dict(tenancy_enabled=True, trusted_proxies="10.0.0.0/8", tenant_bootstrap="m4i,acme,beta",
              oidc_enabled=True, tenant_oidc_issuers=ISS,
              tenant_oidc_jwks_url="http://keycloak:8080/aurelius/auth/realms/{tenant}/protocol/openid-connect/certs",
              typedef_cache_check_secs=0, download_dir=tempfile.mkdtemp(prefix="pyatlas-mt-"),
              import_dir=tempfile.mkdtemp(prefix="pyatlas-mt-imp-"), aurelius_sync_write_timeout_secs=5)
    kw.update(overrides)
    fake = fake or FakeElasticsearch()
    app = create_app(Settings(**kw), es_client=fake)
    return app, fake


@pytest.fixture
def mt(monkeypatch):
    app, fake = mt_app(monkeypatch)
    with TestClient(app, client=PROXY) as c:
        c.fake = fake
        yield c


def docs(c, tenant, name):
    st = c.portal.call(c.app.state.tenants.get, tenant).services.store

    async def dump():
        if not await st.es.indices.exists(index=st.index(name)):
            return []
        return [d async for _id, d in st.scan(st.index(name), {"match_all": {}})]
    return c.portal.call(dump)


def create_domain(c, tenant, qn, name):
    r = c.post(f"{V2}/entity", headers=h(tenant, realm_token(tenant)), json={"entity": {
        "typeName": "m4i_data_domain", "attributes": {"qualifiedName": qn, "name": name}}})
    assert r.status_code == 200, r.text
    return r.json()["mutatedEntities"]["CREATE"][0]["guid"]


def test_tenant_ids():
    assert valid_tenant_id("acme") and valid_tenant_id("m4i") and valid_tenant_id("big-corp2")
    for bad in ("", "a", "Acme", "acme_x", "-acme", "acme-", "auth", "atlas", "kibana", "platform", "x" * 40,
                "a/b", "a.b"):
        assert not valid_tenant_id(bad), bad
    with pytest.raises(ValueError):
        check_tenant_id("atlas")


def test_data_of_one_tenant_is_invisible_to_another(mt):
    c = mt
    acme = create_domain(c, "acme", "acme-domain", "Secret ACME domain")
    beta = create_domain(c, "beta", "beta-domain", "Beta domain")
    # each tenant's indices, nothing shared
    assert c.fake.data["aurelius_acme_entities"].get(acme) and acme not in c.fake.data["aurelius_beta_entities"]
    assert not any(k.startswith("atlas_") for k in c.fake.data)
    t_acme, t_beta = realm_token("acme"), realm_token("beta")
    assert c.get(f"{V2}/entity/guid/{acme}", headers=h("acme", t_acme)).status_code == 200
    assert c.get(f"{V2}/entity/guid/{acme}", headers=h("beta", t_beta)).status_code == 404
    assert c.get(f"{V2}/entity/uniqueAttribute/type/m4i_data_domain", params={"attr:qualifiedName": "acme-domain"},
                 headers=h("beta", t_beta)).status_code == 404
    # searches: basic, DSL, full text, the Aurelius search of the frontend
    for tenant, tok, mine, other in (("acme", t_acme, acme, beta), ("beta", t_beta, beta, acme)):
        r = c.get(f"{V2}/search/basic", params={"typeName": "m4i_data_domain"}, headers=h(tenant, tok)).json()
        guids = {e["guid"] for e in r.get("entities") or []}
        assert mine in guids and other not in guids
        r = c.get(f"{V2}/search/dsl", params={"query": "m4i_data_domain"}, headers=h(tenant, tok)).json()
        assert {e["guid"] for e in r.get("entities") or []} == {mine}
        r = c.get(f"{V2}/search/fulltext", params={"query": "domain"}, headers=h(tenant, tok)).json()
        assert other not in {e["guid"] for e in r.get("entities") or []}
        r = c.post("/api/aurelius/search/atlas-dev", headers=h(tenant, tok), json={"query": "domain"})
        assert r.status_code == 200, r.text
        found = json.dumps(r.json())
        assert mine in found and other not in found
    # audits of an entity of another tenant: nothing
    r = c.get(f"{V2}/entity/{acme}/audit", headers=h("beta", t_beta))
    assert r.status_code in (200, 404) and acme not in json.dumps(r.json() if r.status_code == 200 else {})
    # the same qualifiedName may exist in two tenants
    create_domain(c, "beta", "acme-domain", "Beta's own domain called like ACME's")


def test_tokens_only_count_for_the_realm_of_the_url(mt):
    c = mt
    url = f"{V2}/types/typedefs/headers"
    assert c.get(url, headers=h("acme", realm_token("acme"))).status_code == 200
    # a valid token of realm beta is useless for acme
    r = c.get(url, headers=h("acme", realm_token("beta")))
    assert r.status_code == 401
    # the issuer of acme, but signed with beta's key: signature check against acme's keys fails
    assert c.get(url, headers=h("acme", realm_token("beta", iss=ISS.format(tenant="acme")))).status_code == 401
    # no Basic auth with users-file users in multi-tenant mode
    assert c.get(url, headers=h("acme"), auth=("admin", "admin")).status_code == 401


def test_tenant_header_rules(monkeypatch):
    app, _ = mt_app(monkeypatch)
    tok = realm_token("acme")
    with TestClient(app, client=("192.168.1.9", 1)) as direct:      # not a trusted proxy
        r = direct.get(f"{V2}/types/typedefs/headers", headers=h("acme", tok))
        assert r.status_code == 400 and "not accepted" in r.json()["errorMessage"]
        assert direct.get(f"{V2}/types/typedefs/headers",
                          headers={"Authorization": f"Bearer {tok}"}).status_code == 404    # no tenant
        assert direct.get("/api/atlas/admin/liveness").status_code == 200                    # health checks work
    with TestClient(app, client=PROXY) as c:
        assert c.get(f"{V2}/types/typedefs/headers", headers=h("nobody", tok)).status_code == 404
        assert c.get(f"{V2}/types/typedefs/headers", headers=h("Acme", tok)).status_code == 404
        # two tenant headers (e.g. one smuggled through) are refused
        r = c.get(f"{V2}/types/typedefs/headers",
                  headers=[("X-Aurelius-Tenant", "acme"), ("X-Aurelius-Tenant", "beta"),
                           ("Authorization", f"Bearer {tok}")])
        assert r.status_code == 400
        # a suspended tenant is gone at once for new requests
        reg = app.state.tenants.registry
        c.portal.call(lambda: reg.update("acme", status="suspended"))
        assert c.get(f"{V2}/types/typedefs/headers", headers=h("acme", tok)).status_code == 404
        assert "acme" not in app.state.tenants.loaded


def test_default_tenant_for_requests_without_header(monkeypatch):
    app, _ = mt_app(monkeypatch, tenant_default="m4i")
    with TestClient(app, client=("192.168.1.9", 1)) as c:
        assert c.get(f"{V2}/types/typedefs/headers",
                     headers={"Authorization": f"Bearer {realm_token('m4i')}"}).status_code == 200
        assert c.get(f"{V2}/types/typedefs/headers",
                     headers={"Authorization": f"Bearer {realm_token('acme')}"}).status_code == 401
        assert app.state.tenants.loaded == ["m4i"]


def test_sessions_are_per_tenant(monkeypatch):
    def fake_token(self, username, password):
        realm = self.token_url.split("/realms/")[1].split("/")[0]
        return realm_token(realm, username) if password == "right" else None
    monkeypatch.setattr(KeycloakPasswordAuthenticator, "_token", fake_token)
    app, _ = mt_app(monkeypatch, oidc_password_login=True)
    with TestClient(app, client=PROXY) as c:
        r = c.post("/j_spring_security_check", data={"j_username": "anna", "j_password": "right"},
                   headers=h("acme"))
        assert r.status_code == 200
        assert "ATLASSESSIONID_acme" in r.headers["set-cookie"]
        s = c.get("/api/atlas/admin/session", headers=h("acme")).json()
        assert s["userName"] == "anna"
        # the acme session cookie is sent along to beta, but beta does not read it
        assert c.get(f"{V2}/types/typedefs/headers", headers=h("beta")).status_code == 401
        # a forged cookie: acme's cookie under beta's name is refused (session bound to its tenant)
        c.cookies.set("ATLASSESSIONID_beta", c.cookies.get("ATLASSESSIONID_acme"))
        assert c.get(f"{V2}/types/typedefs/headers", headers=h("beta")).status_code == 401
        # a login to beta gets beta's own session
        c.cookies.delete("ATLASSESSIONID_beta")
        r = c.post("/j_spring_security_check", data={"j_username": "anna", "j_password": "right"},
                   headers=h("beta"))
        assert r.status_code == 200
        assert c.get("/api/atlas/admin/session", headers=h("beta")).json()["userName"] == "anna"
        assert c.get("/api/atlas/admin/session", headers=h("acme")).json()["userName"] == "anna"


def test_access_log_clickstream_and_audits_per_tenant(mt):
    c = mt
    guid = create_domain(c, "acme", "d1", "D1")
    c.post("/api/aurelius/repository/log", headers=h("acme", realm_token("acme")),
           json={"app": "atlas", "timestamp": 1, "url": f"/search/details/{guid}", "userid": "x"})
    c.get(f"{V2}/types/typedefs/headers", headers=h("beta", realm_token("beta", "bob")))
    assert [x["user"] for x in docs(c, "acme", "access")] == ["steward1"]
    assert [x["user"] for x in docs(c, "beta", "access")] == ["bob"]
    assert len(docs(c, "acme", "clickstream")) == 1 and not docs(c, "beta", "clickstream")
    assert guid in json.dumps(docs(c, "acme", "audit"))
    assert guid not in json.dumps(docs(c, "beta", "audit"))


def test_retention_runs_for_every_tenant_loaded_or_not(mt):
    c = mt
    old = int(time.time() * 1000) - 400 * 86400 * 1000
    mgr = c.app.state.tenants
    for t in ("acme", "beta"):
        st = c.portal.call(mgr.get, t).services.store
        c.portal.call(lambda: st.put(st.access, "old", {"user": "old", "timestamp": old, "method": "basic"}))
    c.portal.call(mgr.unload, "beta")
    c.portal.call(lambda: mgr.registry.update("acme", retentionDays=1000))     # acme keeps logins longer
    res = c.portal.call(mgr.apply_retention)
    assert res["beta"]["aurelius_beta_access"] == 1
    assert "old" not in [x["user"] for x in docs(c, "beta", "access")]
    assert "old" in [x["user"] for x in docs(c, "acme", "access")]


def test_idle_contexts_are_unloaded_and_come_back(mt):
    c = mt
    mgr = c.app.state.tenants
    guid = create_domain(c, "acme", "d1", "D1")
    assert "acme" in mgr.loaded
    c.portal.call(mgr.unload, "acme")
    assert "acme" not in mgr.loaded
    assert c.get(f"{V2}/entity/guid/{guid}", headers=h("acme", realm_token("acme"))).status_code == 200
    assert "acme" in mgr.loaded


def test_downloads_are_kept_per_tenant(mt):
    c = mt
    s_acme = c.portal.call(c.app.state.tenants.get, "acme").services
    s_beta = c.portal.call(c.app.state.tenants.get, "beta").services
    assert s_acme.downloads.base_dir != s_beta.downloads.base_dir
    assert str(s_acme.downloads.base_dir).endswith("acme")


def test_log_lines_carry_the_tenant(mt, caplog):
    caplog.handler.addFilter(TenantFilter())
    caplog.set_level(logging.DEBUG, logger="pyatlas.request")
    c = mt
    c.get(f"{V2}/types/typedefs/headers", headers=h("acme", realm_token("acme", "anna")))
    c.get(f"{V2}/types/typedefs/headers", headers=h("beta", realm_token("beta", "bob")))
    recs = [r for r in caplog.records if r.name == "pyatlas.request"]
    assert [(r.tenant, r.user, r.status) for r in recs] == [("acme", "anna", 200), ("beta", "bob", 200)]
    line = json.loads(JsonFormatter().format(recs[0]))
    assert line["tenant"] == "acme" and line["path"] == f"{V2}/types/typedefs/headers" and line["user"] == "anna"
    # no tenant -> no tenant field (the shipper routes such lines to the platform stream)
    rec = logging.LogRecord("pyatlas", logging.WARNING, __file__, 1, "start-up", (), None)
    assert "tenant" not in json.loads(JsonFormatter().format(rec))
    tok = tenant_var.set("acme")
    try:
        assert json.loads(JsonFormatter().format(rec))["tenant"] == "acme"
    finally:
        tenant_var.reset(tok)


def test_single_tenant_mode_is_unchanged(client):
    assert client.app.state.tenants is None
    assert client.get(f"{V2}/types/typedefs/headers").status_code == 200
    assert "test_entities" in client.fake.data


def test_frontend_config_per_tenant(mt):
    c = mt
    r = c.get("/api/aurelius/frontend-config", headers={"X-Aurelius-Tenant": "acme"})
    assert r.status_code == 200
    assert r.json() == {"keycloak": {"url": "/aurelius/auth", "realm": "acme", "clientId": "m4i_atlas"},
                        "tenant": {"id": "acme", "name": "acme"}}
    assert c.get("/api/aurelius/frontend-config", headers={"X-Aurelius-Tenant": "nope"}).status_code == 404


def test_kibana_login_goes_to_the_realm_of_the_tenant(mt):
    c = mt
    cb = "http://localhost:9090/aurelius/kibana-oidc/callback"
    r = c.get("/api/aurelius/kibana-discover", follow_redirects=False, params={
        "oidc_callback": cb, "target_link_uri": "http://localhost:9090/aurelius/kibana/s/acme/app/dashboards",
        "method": "get", "x_csrf": "abc"})
    assert r.status_code == 302
    loc = r.headers["location"]
    assert loc.startswith("/aurelius/kibana-oidc/callback?")
    assert "iss=http%3A%2F%2Flocalhost%3A8080%2Faurelius%2Fauth%2Frealms%2Facme" in loc and "x_csrf=abc" in loc
    r = c.get("/api/aurelius/kibana-discover", follow_redirects=False, params={
        "oidc_callback": cb, "target_link_uri": "http://localhost:9090/aurelius/beta/kibana/"})
    assert "realms%2Fbeta" in r.headers["location"]
    # unknown tenant, no tenant, a foreign callback: no redirect
    for target, callback in (("http://localhost:9090/aurelius/kibana/s/nope/", cb),
                             ("http://localhost:9090/aurelius/kibana/app/home", cb),
                             ("http://localhost:9090/aurelius/kibana/s/acme/", "https://evil.example/x"),
                             ("http://localhost:9090/aurelius/kibana/s/acme/", "https://evil.example/kibana-oidc/callback")):
        r = c.get("/api/aurelius/kibana-discover", follow_redirects=False,
                  params={"oidc_callback": callback, "target_link_uri": target})
        assert r.status_code in (400, 404), (target, callback)
