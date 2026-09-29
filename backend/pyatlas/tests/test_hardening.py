"""Hardening round (29 Sep 2026): privileges of Keycloak users, file users off, limits, retention."""
import time

from pyatlas.oidc import JwksCache, KeycloakPasswordAuthenticator
from tests.conftest import _fresh_client
from tests.test_oidc import ISS, JWK, bearer, token

V2 = "/api/atlas/v2"


def oidc_client(monkeypatch, **kw):
    monkeypatch.setattr(JwksCache, "_http_fetch", lambda self: {"keys": [JWK]})
    c = _fresh_client(oidc_enabled=True, oidc_issuers=ISS, **kw)
    c.auth = None
    return c


def test_keycloak_user_named_like_a_file_user_gets_only_its_token_roles(monkeypatch):
    c = oidc_client(monkeypatch)
    try:
        # "admin" has ROLE_ADMIN through userRoles of the policy file - not for a Keycloak user of that name
        t = token("admin", ())
        assert c.post("/api/atlas/admin/export", headers=bearer(t), json={"itemsToExport": []}).status_code == 403
        assert c.post("/api/aurelius/search/atlas-dev", headers=bearer(t), json={}).status_code == 403
        assert c.get("/api/aurelius/data_governance_dashboard", headers=bearer(t)).status_code == 403
        assert c.get("/api/lin_api/kubernetes/kubernetes_pod/", headers=bearer(t)).status_code == 403
        # with an Aurelius role the search works; the index status stays for admins
        sci = token("scientist1", ("DATA_SCIENTIST",))
        assert c.post("/api/aurelius/search/atlas-dev", headers=bearer(sci), json={}).status_code == 200
        assert c.get("/api/aurelius/admin/search/status", headers=bearer(sci)).status_code == 403
    finally:
        c.__exit__(None, None, None)


def test_users_file_can_be_switched_off(monkeypatch):
    c = oidc_client(monkeypatch, file_users_enabled=False)
    try:
        assert c.get(f"{V2}/types/typedefs/headers", auth=("admin", "admin")).status_code == 401
        assert c.get(f"{V2}/types/typedefs/headers", headers=bearer(token())).status_code == 200
    finally:
        c.__exit__(None, None, None)


def test_basic_auth_with_keycloak_passwords_is_cached(monkeypatch):
    calls = []

    def fake_token(self, username, password):
        calls.append(username)
        return token(username, ("DATA_STEWARD",)) if password == "right" else None
    monkeypatch.setattr(KeycloakPasswordAuthenticator, "_token", fake_token)
    c = oidc_client(monkeypatch, oidc_password_login=True, file_users_enabled=False,
                    oidc_jwks_url="http://keycloak:8080/aurelius/auth/realms/m4i/protocol/openid-connect/certs")
    try:
        for _ in range(3):
            assert c.get(f"{V2}/types/typedefs/headers", auth=("steward", "right")).status_code == 200
        assert calls == ["steward"]                # one Keycloak login, not one per request
        assert c.get(f"{V2}/types/typedefs/headers", auth=("steward", "wrong")).status_code == 401
    finally:
        c.__exit__(None, None, None)


def test_json_bodies_are_limited():
    c = _fresh_client(max_json_mb=1)
    try:
        big = {"entity": {"typeName": "m4i_data_domain", "attributes": {"qualifiedName": "x", "name": "x" * (2 << 20)}}}
        r = c.post(f"{V2}/entity", json=big)
        assert r.status_code == 400 and "larger than 1 MB" in r.text
    finally:
        c.__exit__(None, None, None)


def test_clickstream_is_limited_per_user():
    c = _fresh_client(clickstream_max_per_minute=5)
    try:
        for i in range(8):
            assert c.post("/api/aurelius/repository/log", json={"app": "atlas", "url": f"/search/browse?{i}"}) \
                .status_code == 204
        st = c.app.state.services.store
        assert c.portal.call(st.count, st.index("clickstream"), {"match_all": {}}) == 5
    finally:
        c.__exit__(None, None, None)


def test_old_logins_and_page_views_are_deleted():
    c = _fresh_client(access_log_retention_days=30, clickstream_retention_days=30)
    try:
        s = c.app.state.services
        st = s.store
        old = int((time.time() - 40 * 86400) * 1000)
        new = int(time.time() * 1000)

        async def seed():
            await st.put(st.access, "old", {"user": "u", "timestamp": old}, refresh="true")
            await st.put(st.access, "new", {"user": "u", "timestamp": new}, refresh="true")
            await st.put(st.index("clickstream"), "old", {"user": "u", "timestamp": old}, refresh="true")
        c.portal.call(seed)
        deleted = c.portal.call(s.apply_retention)
        assert deleted == {st.access: 1, st.index("clickstream"): 1}
        assert c.portal.call(st.get, st.access, "new") is not None
    finally:
        c.__exit__(None, None, None)
