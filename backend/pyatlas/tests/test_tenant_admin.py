"""aurelius-admin: what a tenant gets in Keycloak, Elasticsearch, Kibana and the proxy (against recorded HTTP)."""
import asyncio
import base64
import json
import re

import pytest

from pyatlas.kibana_objects import saved_objects
from pyatlas.tenant_admin import (Admin, AdminError, Config, issuer_filename, kibana_key_descriptor, logs_pipeline,
                                  pyatlas_key_descriptor, realm_representation)
from tests.fake_es import FakeElasticsearch


class FakeHttp:
    """Keycloak, Elasticsearch and Kibana as far as aurelius-admin uses them."""

    def __init__(self):
        self.calls = []
        self.realms, self.clients, self.users, self.spaces, self.keys = {}, {}, {}, set(), {}
        self.imports = {}

    def __call__(self, method, url, headers, body):
        data = json.loads(body) if body and headers.get("Content-Type") == "application/json" else body
        path = url.split("://", 1)[1].split("/", 1)[1]
        path = "/" + path
        self.calls.append((method, path))
        if "/realms/master/protocol/openid-connect/token" in path:
            return 200, json.dumps({"access_token": "t", "expires_in": 60}).encode()
        m = re.match(r"^/aurelius/auth/admin/realms(?:/([^/?]+))?(/.*)?$", path.split("?")[0])
        if m:
            return self._keycloak(method, m.group(1), m.group(2) or "", path, data)
        if "/.well-known/openid-configuration" in path:
            realm = path.split("/realms/")[1].split("/")[0]
            return 200, json.dumps({"issuer": f"http://localhost:9090/aurelius/auth/realms/{realm}"}).encode()
        if url.startswith("http://kibana"):
            return self._kibana(method, path, data)
        return self._es(method, path, data, headers)

    def _keycloak(self, method, realm, rest, path, data):
        if realm is None and method == "POST":
            self.realms[data["realm"]] = data
            self.clients[data["realm"]] = {c["clientId"]: {**c, "id": c["clientId"] + "-id"}
                                           for c in data.get("clients", [])}
            return 201, b""
        if realm not in self.realms:
            return 404, b"{}"
        if rest == "" and method == "GET":
            return 200, json.dumps({"id": realm, **self.realms[realm]}).encode()
        if rest == "" and method in ("PUT", "DELETE"):
            if method == "DELETE":
                del self.realms[realm]
            else:
                self.realms[realm].update(data)
            return 204, b""
        if rest == "/clients" and method == "GET":
            cid = path.split("clientId=")[1]
            c = self.clients[realm].get(cid)
            return 200, json.dumps([c] if c else []).encode()
        if rest == "/clients" and method == "POST":
            self.clients[realm][data["clientId"]] = {**data, "id": data["clientId"] + "-id"}
            return 201, b""
        if rest.startswith("/clients/") and rest.endswith("/client-secret"):
            cid = rest.split("/")[2][:-3]
            return 200, json.dumps({"value": self.clients[realm][cid].get("secret")}).encode()
        if rest.startswith("/clients/") and method == "PUT":
            self.clients[realm][data["clientId"]].update(data)
            return 204, b""
        if rest.startswith("/roles/"):
            return 200, json.dumps({"id": "r-" + rest.split("/")[2], "name": rest.split("/")[2]}).encode()
        if rest == "/users" and method == "GET":
            name = path.split("username=")[1]
            u = self.users.get((realm, name))
            return 200, json.dumps([u] if u else []).encode()
        if rest == "/users" and method == "POST":
            self.users[(realm, data["username"])] = {"id": "u-" + data["username"], **data}
            return 201, b""
        return 204, b""

    def _es(self, method, path, data, headers):
        if path == "/_security/api_key" and method == "POST":
            kid = f"k{len(self.keys) + 1}"
            encoded = base64.b64encode(f"{kid}:secret".encode()).decode()
            self.keys[encoded] = {"id": kid, **data}
            return 200, json.dumps({"id": kid, "encoded": encoded}).encode()
        if path == "/_security/_authenticate":
            key = headers.get("Authorization", "").split(" ", 1)[1]
            return (200, b"{}") if key in self.keys else (401, b"{}")
        if path == "/_security/api_key" and method == "DELETE":
            for enc, k in list(self.keys.items()):
                if k["id"] in data["ids"]:
                    del self.keys[enc]
            return 200, b"{}"
        if method == "HEAD":
            return 404, b""
        if path.startswith("/_enrich/policy/") and method == "GET":
            return 404, b"{}"
        return 200, b"{}"

    def _kibana(self, method, path, data):
        if path.endswith("/api/status"):
            return 200, json.dumps({"status": {"overall": {"level": "available"}}}).encode()
        m = re.match(r"^/aurelius/kibana/api/spaces/space(?:/(.+))?$", path)
        if m:
            if method == "GET":
                return (200, b"{}") if m.group(1) in self.spaces else (404, b"{}")
            if method == "DELETE":
                self.spaces.discard(m.group(1))
                return 204, b""
            self.spaces.add(data["id"])
            return 200, b"{}"
        m = re.match(r"^/aurelius/kibana/s/([^/]+)/api/saved_objects/_import", path)
        if m:
            text = data.decode()
            self.imports[m.group(1)] = [json.loads(line) for line in text.replace("\r\n", "\n").split("\n") if line.startswith("{")]
            return 200, json.dumps({"success": True}).encode()
        return 200, b"{}"


@pytest.fixture
def admin(tmp_path):
    http = FakeHttp()
    cfg = Config(public_url="http://localhost:9090", keycloak_url="http://keycloak:8080/aurelius/auth",
                 keycloak_admin_password="pw", es_url="http://elasticsearch:9200", es_password="pw",
                 kibana_url="http://kibana:5601/aurelius/kibana", tenants_dir=tmp_path, operator_password="op")
    a = Admin(cfg, transport=http, es_client=FakeElasticsearch())
    asyncio.run(a._registry().bootstrap())
    a.http = http
    return a


def run(coro):
    return asyncio.run(coro)


def test_realm_template():
    rep = realm_representation("acme", "ACME", Config(public_url="https://x.example"), "s3cret")
    assert rep["id"] == rep["realm"] == "acme"
    assert {r["name"] for r in rep["roles"]["realm"]} == {"ROLE_ADMIN", "DATA_STEWARD", "DATA_SCIENTIST"}
    front, proxy = rep["clients"]
    assert front["redirectUris"] == ["https://x.example/aurelius/acme/atlas/*"] and front["publicClient"]
    assert proxy["redirectUris"] == ["https://x.example/aurelius/kibana-oidc/callback"] and proxy["secret"] == "s3cret"
    assert rep["eventsEnabled"] and "jboss-logging" in rep["eventsListeners"] and rep["bruteForceProtected"]


def test_keys_reach_only_the_tenant():
    (d,) = pyatlas_key_descriptor("acme").values()
    assert d["indices"] == [{"names": ["aurelius_acme_*"], "privileges": ["all"]}] and "cluster" not in d
    (k,) = kibana_key_descriptor("acme").values()
    assert k["indices"][0]["names"] == ["aurelius_acme_*", "logs-aurelius.*-acme"]
    assert set(k["indices"][0]["privileges"]) == {"read", "view_index_metadata"}
    assert k["applications"][0]["resources"] == ["space:acme"]
    (p,) = kibana_key_descriptor("platform", all_tenants=True).values()
    assert "aurelius_*" in p["indices"][0]["names"]


def test_issuer_file_names_of_mod_auth_openidc():
    assert issuer_filename("https://host.example/aurelius/auth/realms/acme") == \
        "host.example%2Faurelius%2Fauth%2Frealms%2Facme"
    assert issuer_filename("http://localhost:9090/aurelius/auth/realms/m4i/") == \
        "localhost%3A9090%2Faurelius%2Fauth%2Frealms%2Fm4i"


def test_log_pipeline_routes_unknown_tenants_to_platform():
    p = logs_pipeline()
    kinds = [list(x)[0] for x in p["processors"]]
    assert kinds[-1] == "reroute" and "enrich" in kinds
    assert p["processors"][-1]["reroute"] == {"dataset": "{{aurelius.dataset}}", "namespace": "{{tenant}}"}
    script = [x["script"]["source"] for x in p["processors"] if "script" in x][1]
    assert "ctx.tenant = 'platform'" in script
    assert p["on_failure"][-1]["reroute"]["namespace"] == "platform"


def test_create_a_tenant(admin):
    rec = run(admin.tenant_create("acme", "ACME Corp", admin_user="anna", admin_email="anna@acme.example"))
    h = admin.http
    assert rec["status"] == "active" and rec["realmId"] == "acme" and rec["esApiKey"]
    assert "acme" in h.realms and ("acme", "anna") in h.users
    assert h.users[("acme", "anna")]["credentials"][0]["temporary"] is True
    # pyatlas key (all on aurelius_acme_*) and Kibana key (read + space) - two keys
    names = sorted(k["name"] for k in h.keys.values())
    assert names == ["aurelius-acme-kibana", "aurelius-acme-pyatlas"]
    # Kibana space with data views on the tenant's indices and log data streams, and the three dashboards
    assert "acme" in h.spaces
    objs = {o["id"]: o for o in h.imports["acme"]}
    assert objs["pyatlas-access"]["attributes"]["title"] == "aurelius_acme_access"
    assert objs["logs-keycloak"]["attributes"]["title"] == "logs-aurelius.keycloak-acme"
    assert {"aurelius-activity", "aurelius-usage", "aurelius-health"} <= set(objs)
    assert not any("beta" in json.dumps(o) or "aurelius_*" in json.dumps(o) for o in objs.values())
    # proxy files: the realm as login provider, the tenant's Kibana key
    oidc = admin.cfg.tenants_dir / "oidc"
    base = "localhost%3A9090%2Faurelius%2Fauth%2Frealms%2Facme"
    assert (oidc / f"{base}.provider").exists()
    client = json.loads((oidc / f"{base}.client").read_text())
    assert client["client_id"] == "aurelius_proxy" and client["client_secret"] == h.clients["acme"]["aurelius_proxy"]["secret"]
    keys = admin.files.keys()
    assert h.keys[keys["acme"]]["name"] == "aurelius-acme-kibana"
    # the tenant's log retention
    assert ("PUT", "/_index_template/logs-aurelius-acme") in h.calls


def test_create_again_keeps_keys_and_users(admin):
    first = run(admin.tenant_create("acme", "ACME"))
    n_keys = len(admin.http.keys)
    again = run(admin.tenant_create("acme", "ACME"))
    assert again["esApiKey"] == first["esApiKey"] and len(admin.http.keys) == n_keys
    # a revoked key is replaced (and the old one invalidated)
    del admin.http.keys[first["esApiKey"]]
    third = run(admin.tenant_create("acme", "ACME"))
    assert third["esApiKey"] != first["esApiKey"]


def test_existing_single_tenant_realm_is_adopted(admin):
    admin.http.realms["m4i"] = {"realm": "m4i", "displayName": "Aurelius Atlas"}
    admin.http.clients["m4i"] = {"m4i_atlas": {"id": "m4i_atlas-id", "clientId": "m4i_atlas", "publicClient": True,
                                               "redirectUris": ["http://localhost:9090/aurelius/atlas/*"]}}
    run(admin.tenant_create("m4i", "M4I", legacy_urls=True))
    uris = admin.http.clients["m4i"]["m4i_atlas"]["redirectUris"]
    assert "http://localhost:9090/aurelius/m4i/atlas/*" in uris and "http://localhost:9090/aurelius/atlas/*" in uris
    assert "aurelius_proxy" in admin.http.clients["m4i"]
    assert admin.http.realms["m4i"]["displayName"] == "Aurelius Atlas"     # kept


def test_platform_init(admin):
    run(admin.platform_init())
    h = admin.http
    assert ("PUT", "/_ingest/pipeline/aurelius-logs") in h.calls
    assert ("PUT", "/_index_template/logs-aurelius") in h.calls
    assert ("PUT", "/_security/role/aurelius_pyatlas") in h.calls
    assert "platform" in h.realms and ("platform", "operator") in h.users
    assert h.users[("platform", "operator")]["credentials"][0] == {"type": "password", "value": "op",
                                                                    "temporary": False}
    objs = {o["id"]: o for o in h.imports["platform"]}
    assert objs["pyatlas-access"]["attributes"]["title"] == "aurelius_*_access"
    assert "tenant" in json.loads(objs["pyatlas-access"]["attributes"]["runtimeFieldMap"])
    assert "platform" in admin.files.keys()


def test_platform_realm_is_not_a_tenant(admin):
    with pytest.raises((AdminError, ValueError)):
        run(admin.tenant_create("platform"))
    with pytest.raises(ValueError):
        run(admin.tenant_create("Bad_Id"))


def test_suspend_and_delete(admin):
    rec = run(admin.tenant_create("acme", "ACME"))
    run(admin.tenant_status("acme", "suspended"))
    assert admin.http.realms["acme"]["enabled"] is False
    assert run(admin._registry().get("acme"))["status"] == "suspended"
    run(admin.tenant_delete("acme"))
    h = admin.http
    assert "acme" not in h.realms and "acme" not in h.spaces and "acme" not in admin.files.keys()
    assert rec["esApiKey"] not in h.keys and not h.keys
    assert ("DELETE", "/aurelius_acme_*?expand_wildcards=all&allow_no_indices=true") in h.calls
    assert ("DELETE", "/_data_stream/logs-aurelius.*-acme") in h.calls
    assert run(admin._registry().get("acme")) is None
    assert not list((admin.cfg.tenants_dir / "oidc").glob("*acme*"))


def test_dry_run_changes_nothing(admin):
    admin.cfg.dry_run = True
    for part in (admin.kc.http, admin.es.http, admin.kibana.http):
        part.dry_run = True
    run(admin.tenant_create("acme", "ACME"))
    assert "acme" not in admin.http.realms and not admin.http.keys
    assert not [c for c in admin.http.calls if c[0] not in ("GET", "HEAD", "POST") or "token" in c[1]
                and False]
    assert all(c[0] in ("GET", "HEAD") or "openid-connect/token" in c[1] or "_authenticate" in c[1]
               for c in admin.http.calls)


def test_saved_objects_of_a_tenant_and_single_tenant_file():
    objs = saved_objects("aurelius_acme", "acme")
    views = [o for o in objs if o["type"] == "index-pattern"]
    assert all("acme" in o["attributes"]["title"] for o in views)
    lens_refs = {r["id"] for o in objs if o["type"] == "lens" for r in o["references"]}
    assert lens_refs <= {o["id"] for o in views}
    dash_refs = {r["id"] for o in objs if o["type"] == "dashboard" for r in o["references"]}
    assert dash_refs <= {o["id"] for o in objs if o["type"] == "lens"}


def test_proxy_sync_writes_the_proxy_files_from_the_registry(admin, tmp_path):
    from pyatlas.tenant_admin import ProxyFiles, proxy_sync
    run(admin.platform_init())
    run(admin.tenant_create("acme", "ACME"))
    run(admin.tenant_create("beta", "Beta"))
    # a proxy elsewhere (Kubernetes sidecar): its own folder, filled from the registry only
    other = ProxyFiles(Config(**{**admin.cfg.__dict__, "tenants_dir": tmp_path / "sidecar"}))
    res = run(proxy_sync(admin, other))
    assert res["realms"] == 3
    assert set(other.keys()) == {"acme", "beta", "platform"}
    assert other.keys() == admin.files.keys()
    oidc = sorted(p.name for p in (tmp_path / "sidecar" / "oidc").iterdir())
    assert len(oidc) == 9 and any("realms%2Fbeta.client" in n for n in oidc)
    # nothing changed -> nothing written; a suspended tenant disappears from the proxy
    assert run(proxy_sync(admin, other))["changed"] == 0
    run(admin.tenant_status("beta", "suspended"))
    run(proxy_sync(admin, other))
    assert set(other.keys()) == {"acme", "platform"}
    assert not any("beta" in p.name for p in (tmp_path / "sidecar" / "oidc").iterdir())
    # secrets never in an export or "show"
    rec = run(admin._registry().get("acme"))
    assert rec["proxyClientSecret"] and rec["kibanaApiKey"]
