"""Keycloak (OIDC) bearer tokens: what the Aurelius frontend sends to /api/atlas."""
import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from pyatlas.oidc import JwksCache
from tests.conftest import _fresh_client

ISS = "http://localhost:8080/aurelius/auth/realms/m4i"
V2 = "/api/atlas/v2"
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0"}


def _key(kid):
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(k.public_key()))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return k, jwk


KEY, JWK = _key("k1")
OTHER, _ = _key("k1")               # same kid, different key: a forged signature
ROTATED, JWK2 = _key("k2")


class _Jwks:
    keys = [JWK]
    calls = 0


@pytest.fixture
def oidc_client(monkeypatch):
    _Jwks.keys, _Jwks.calls = [JWK], 0

    def fetch(self):
        _Jwks.calls += 1
        return {"keys": list(_Jwks.keys)}
    monkeypatch.setattr(JwksCache, "_http_fetch", fetch)
    c = _fresh_client(oidc_enabled=True, oidc_issuers=f"{ISS},https://example.com/aurelius/auth/realms/m4i")
    c.auth = None
    yield c
    c.__exit__(None, None, None)


def token(user="steward1", roles=("DATA_STEWARD",), key=KEY, kid="k1", alg="RS256", **claims):
    now = int(time.time())
    body = {"iss": ISS, "sub": "f:1", "typ": "Bearer", "azp": "m4i_atlas", "iat": now, "exp": now + 300,
            "preferred_username": user, "realm_access": {"roles": list(roles) + ["offline_access"]}}
    body.update(claims)
    return jwt.encode(body, key, algorithm=alg, headers={"kid": kid})


def bearer(t):
    return {"Authorization": f"Bearer {t}", **BROWSER}


def test_keycloak_token_authenticates_with_realm_roles(oidc_client):
    c = oidc_client
    r = c.get(f"{V2}/types/typedef/name/m4i_data_domain", headers=bearer(token()))
    assert r.status_code == 200, r.text
    # a steward may create entities; no session cookie and no CSRF header are needed for bearer tokens
    r = c.post(f"{V2}/entity", headers=bearer(token()), json={"entity": {"typeName": "m4i_data_domain", "attributes": {
        "qualifiedName": "d1", "name": "Domain 1"}}})
    assert r.status_code == 200, r.text
    assert "ATLASSESSIONID" not in r.headers.get("set-cookie", "")
    guid = r.json()["mutatedEntities"]["CREATE"][0]["guid"]
    e = c.get(f"{V2}/entity/guid/{guid}", headers=bearer(token())).json()["entity"]
    assert e["createdBy"] == "steward1"


def test_roles_decide_what_a_user_may_do(oidc_client):
    c = oidc_client
    body = {"entity": {"typeName": "m4i_data_domain", "attributes": {"qualifiedName": "d2", "name": "D2"}}}
    r = c.post(f"{V2}/entity", headers=bearer(token("scientist1", ("DATA_SCIENTIST",))), json=body)
    assert r.status_code == 403, r.text
    assert c.get(f"{V2}/types/typedef/name/m4i_person", headers=bearer(token("scientist1", ("DATA_SCIENTIST",)))) \
        .status_code == 200
    # admin operations need ROLE_ADMIN
    exp = {"itemsToExport": [{"typeName": "m4i_data_domain", "uniqueAttributes": {"qualifiedName": "none"}}]}
    assert c.post("/api/atlas/admin/export", headers=bearer(token("steward1")), json=exp).status_code == 403
    assert c.post("/api/atlas/admin/export", headers=bearer(token("admin1", ("ROLE_ADMIN",))), json=exp) \
        .status_code != 403
    # no roles at all: authenticated, but nothing is allowed
    assert c.get(f"{V2}/types/typedef/name/m4i_person", headers=bearer(token("nobody", ()))).status_code == 403


@pytest.mark.parametrize("bad", [
    lambda: token(exp=int(time.time()) - 3600),                               # expired
    lambda: token(iss="http://evil.example/realms/m4i"),                      # other issuer
    lambda: token(key=OTHER),                                                 # forged signature
    lambda: token(typ="Refresh"),                                             # not an access token
    lambda: token(kid="unknown"),                                             # unknown key
    lambda: jwt.encode({"iss": ISS, "exp": int(time.time()) + 60, "preferred_username": "admin",
                        "realm_access": {"roles": ["ROLE_ADMIN"]}}, "secret", algorithm="HS256",
                       headers={"kid": "k1"}),                                # symmetric algorithm
    lambda: "not-a-jwt",
])
def test_invalid_tokens_are_rejected(oidc_client, bad):
    r = oidc_client.get(f"{V2}/types/typedefs/headers", headers=bearer(bad()))
    assert r.status_code == 401
    assert "invalid_token" in r.headers["www-authenticate"]


def test_unsigned_token_is_rejected(oidc_client):
    t = jwt.encode({"iss": ISS, "exp": int(time.time()) + 60, "preferred_username": "admin",
                    "realm_access": {"roles": ["ROLE_ADMIN"]}}, None, algorithm="none")
    assert oidc_client.get(f"{V2}/types/typedefs/headers", headers=bearer(t)).status_code == 401


def test_key_rotation_and_second_issuer(oidc_client, monkeypatch):
    c = oidc_client
    assert c.get(f"{V2}/types/typedefs/headers", headers=bearer(token())).status_code == 200
    _Jwks.keys = [JWK, JWK2]                       # Keycloak rotated its key
    t2 = token(key=ROTATED, kid="k2", iss="https://example.com/aurelius/auth/realms/m4i")
    # an unknown key id makes pyatlas re-read the key set (once the minimum refresh interval has passed)
    orig = JwksCache.key

    def after_interval(self, kid):
        self._loaded -= 60
        return orig(self, kid)
    monkeypatch.setattr(JwksCache, "key", after_interval)
    assert c.get(f"{V2}/types/typedefs/headers", headers=bearer(t2)).status_code == 200
    assert _Jwks.calls == 2


def test_client_restriction(monkeypatch):
    monkeypatch.setattr(JwksCache, "_http_fetch", lambda self: {"keys": [JWK]})
    c = _fresh_client(oidc_enabled=True, oidc_issuers=ISS, oidc_clients="m4i_atlas")
    c.auth = None
    try:
        assert c.get(f"{V2}/types/typedefs/headers", headers=bearer(token())).status_code == 200
        assert c.get(f"{V2}/types/typedefs/headers", headers=bearer(token(azp="other"))).status_code == 401
        assert c.get(f"{V2}/types/typedefs/headers",
                     headers=bearer(token(azp="other", aud=["m4i_atlas"]))).status_code == 200
    finally:
        c.__exit__(None, None, None)


def test_bearer_without_oidc_configuration(client):
    client.auth = None
    r = client.get(f"{V2}/types/typedefs/headers", headers=bearer(token()))
    assert r.status_code == 401 and "not configured" in r.json()["errorMessage"]
    # file users (Basic auth) keep working next to OIDC
    assert client.get(f"{V2}/types/typedefs/headers", auth=("admin", "admin")).status_code == 200


def test_frontend_clickstream_and_error_reports(oidc_client, caplog):
    import logging
    caplog.set_level(logging.INFO, logger="pyatlas.aurelius")
    r = oidc_client.post("/api/aurelius/repository/log", headers=bearer(token()),
                         json={"app": "atlas", "timestamp": 1, "url": "/search/browse", "userid": "someone-else"})
    assert r.status_code == 204
    r = oidc_client.post("/api/aurelius/repository/error", headers=bearer(token()),
                         json={"app": "atlas", "version": "1", "error": {"message": "boom", "stack": "x"}})
    assert r.status_code == 204
    events = [json.loads(rec.getMessage()) for rec in caplog.records if rec.name.startswith("pyatlas.aurelius")]
    assert events[0] == {"type": "clickstream", "user": "steward1", "app": "atlas", "url": "/search/browse",
                         "timestamp": 1}
    assert events[1]["message"] == "boom" and events[1]["user"] == "steward1"
    # anonymous callers are rejected like every other API call
    assert oidc_client.post("/api/aurelius/repository/log", json={}).status_code == 401
