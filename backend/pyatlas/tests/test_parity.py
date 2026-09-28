"""Phase 0: the m4i (Aurelius) type definitions and the parity tools, checked against pyatlas itself."""
import copy
import json
import os
import zipfile

import pytest

from parity.diff import Rules, diff
from parity.indices import allowlist_for, compare_documents
from parity.mutations import compare_manifests, run_scenario
from parity.replay import AURELIUS_REWRITES, Recorded, read_recording, replay, rewrite
from parity.store import ZipSource, compare_store, compare_typedefs
from tests.conftest import _fresh_client
from tests.parity_adapter import TestClientAdapter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST_INSTALL = os.path.join(HERE, "..", "m4i-atlas-post-install", "data")
REPO_ZIP = os.path.join(POST_INSTALL, "sample_data.zip")
GOLDEN = os.path.join(POST_INSTALL, "atlas-dev.json")
V2 = "/api/atlas/v2"
M4I_TYPES = ("m4i_referenceable", "m4i_person", "m4i_data_domain", "m4i_data_entity", "m4i_data_attribute",
             "m4i_system", "m4i_collection", "m4i_dataset", "m4i_field", "m4i_data_quality",
             "m4i_gov_data_quality", "m4i_generic_process", "m4i_kafka_topic", "m4i_kubernetes_pod")
need_repo_zip = pytest.mark.skipif(not os.path.exists(REPO_ZIP), reason="Aurelius sample data not in the monorepo")


# ---------------------------------------------------------------------------------------------- m4i models
def test_m4i_types_are_loaded_at_startup(client):
    names = {d["name"] for d in client.get(f"{V2}/types/typedefs").json()["entityDefs"]}
    assert set(M4I_TYPES) <= names
    rel = client.get(f"{V2}/types/relationshipdef/name/m4i_data_entity_assignment").json()
    assert {rel["endDef1"]["name"], rel["endDef2"]["name"]} == {"dataEntity", "dataDomain"}
    assert client.get(f"{V2}/types/classificationdef/name/PII").status_code == 200


@need_repo_zip
def test_m4i_models_match_the_typedefs_of_the_aurelius_sample_export(client):
    """Gate of phase 0: the model files define the m4i types exactly as the running Aurelius Atlas does."""
    src = ZipSource(REPO_ZIP)
    zip_td = src.typedefs()
    m4i = {d["name"] for c in zip_td.values() if isinstance(c, list) for d in c
           if d["name"].startswith("m4i_") or d["name"] in ("PII", "key_data", "low_risk", "medium_risk",
                                                             "high_risk")}
    from parity.report import Report
    report = Report("typedefs", src.name, "pyatlas models")
    compare_typedefs(zip_td, client.get(f"{V2}/types/typedefs").json(), report, names=m4i)
    assert report.checked == len(m4i) > 30
    assert report.passed, json.dumps([f.as_dict() for f in report.findings], indent=1)[:3000]


def test_models_are_in_sync_with_m4i_atlas_core():
    """Regenerating the model files from libs/m4i-atlas-core gives the committed files (when importable)."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("gen_m4i_models", os.path.join(HERE, "scripts", "gen_m4i_models.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    try:
        sources = gen.load_sources()
    except ImportError as e:
        pytest.skip(f"m4i-atlas-core not importable here ({e})")
    finally:
        sys.path[:] = [p for p in sys.path if not p.endswith("m4i-atlas-core")]
    for stem, d in sources.items():
        with open(os.path.join(HERE, "models", "9000-Aurelius", f"{stem}.json"), encoding="utf-8") as f:
            assert json.load(f) == d, f"{stem}.json is out of date: run scripts/gen_m4i_models.py"


# ---------------------------------------------------------------------------------------------- diff
def test_diff_rules():
    a = {"x": 1, "t": {"updateTime": 5, "l": [1, 2, 3]}, "e": None, "s": ["a", "b"], "f": 0.30000001}
    b = {"x": 1, "t": {"updateTime": 9, "l": [1, 2, 3]}, "s": ["b", "a"], "f": 0.3}
    assert [d.where for d in diff(a, b)] == ["f", "s[0]", "s[1]", "t.updateTime"]
    rules = Rules(ignore=["**.updateTime"], unordered=["s"], float_tolerance=1e-6)
    assert diff(a, b, rules) == []
    assert [d.where for d in diff({"s": ["a", "c"]}, {"s": ["a", "d"]}, rules)] == ["s.*"]
    assert [d.as_dict()["right"] for d in diff({"s": ["a"]}, {"s": ["a", "z"]}, rules)] == ["z"]


# ---------------------------------------------------------------------------------------------- check 1
@need_repo_zip
def test_store_check_passes_after_import_and_finds_changes(client):
    with open(REPO_ZIP, "rb") as f:
        r = client.post("/api/atlas/admin/import", files={"data": ("sample_data.zip", f, "application/zip")})
    assert r.json()["operationStatus"] == "SUCCESS"
    target = TestClientAdapter(client)
    report = compare_store(ZipSource(REPO_ZIP), target)
    assert report.passed, json.dumps([f.as_dict() for f in report.findings[:5]], indent=1)
    assert report.stats["entities total"] == len(ZipSource(REPO_ZIP).order) > 600

    # the check notices a changed attribute, a removed relationship and a deleted entity
    order = ZipSource(REPO_ZIP).order
    ents = {g: client.get(f"{V2}/entity/guid/{g}").json()["entity"] for g in order[:200]}
    changed = next(g for g, e in ents.items() if e["typeName"] == "m4i_data_attribute")
    client.put(f"{V2}/entity/guid/{changed}", params={"name": "definition"}, json="changed by the test")
    deleted = next(g for g, e in ents.items() if e["typeName"] == "m4i_person")
    client.delete(f"{V2}/entity/guid/{deleted}")
    report = compare_store(ZipSource(REPO_ZIP), target, with_typedefs=False)
    items = {f.item: f for f in report.findings}
    assert changed in items and any(d["path"] == "attributes.definition" for d in items[changed].details)
    assert deleted in items and any(d["path"] == "status" for d in items[deleted].details)
    assert not report.passed


# ---------------------------------------------------------------------------------------------- check 2
@pytest.mark.skipif(not os.path.exists(GOLDEN), reason="golden App Search documents not in the monorepo")
def test_index_check_on_the_golden_documents():
    with open(GOLDEN, encoding="utf-8") as f:
        golden = json.load(f)
    rules = allowlist_for("atlas-dev")
    assert compare_documents(golden, copy.deepcopy(golden), rules).passed
    other = copy.deepcopy(golden)
    other[0]["breadcrumbname"] = list(reversed(other[0]["breadcrumbname"])) + ["x"]      # ordered: a difference
    other[1]["derivedperson"] = list(reversed(other[1]["derivedperson"]))                  # a set: no difference
    other[2]["dqscore_overall"] = (other[2]["dqscore_overall"] or 0) + 0.00001             # within tolerance
    removed = other.pop(3)
    report = compare_documents(golden, other, rules)
    assert {f.item for f in report.findings} == {golden[0]["id"], removed["id"]}
    # every golden document belongs to an entity of the sample export (they are the same data set)
    if os.path.exists(REPO_ZIP):
        guids = set(ZipSource(REPO_ZIP).order)
        assert {d["guid"] for d in golden} <= guids


# ---------------------------------------------------------------------------------------------- check 3
def test_same_changes_give_the_same_results():
    manifests = []
    for _ in range(2):
        c = _fresh_client()
        try:
            manifests.append(run_scenario(TestClientAdapter(c)))
        finally:
            c.__exit__(None, None, None)
    a, b = manifests
    assert a["tag"] != b["tag"] and len(a["entities"]) == 13
    assert [s["step"] for s in a["steps"]][-1] == "delete field"
    report = compare_manifests(a, b)
    assert report.passed, json.dumps([f.as_dict() for f in report.findings], indent=1)[:3000]
    moved = next(e for qn, e in a["entities"].items() if qn.endswith("attr2"))
    assert [r["displayText"] for r in moved["relationshipAttributes"]["dataEntity"]] == ["ent2"]
    field2 = next(e for qn, e in a["entities"].items() if qn.endswith("field2"))
    assert field2 is None or field2["status"] == "DELETED"

    # a server that behaves differently is caught
    b2 = copy.deepcopy(b)
    e = next(e for qn, e in b2["entities"].items() if qn.endswith("--dom"))
    e["attributes"]["name"] = "not renamed"
    report = compare_manifests(a, b2)
    assert [f.item for f in report.findings] == ["parity<tag>--dom"]


# ---------------------------------------------------------------------------------------------- check 4
def test_replay_recorded_responses(client, tmp_path):
    from tests.helpers import create_sales_model
    ga = create_sales_model(client)
    target = TestClientAdapter(client)
    records = []
    for method, path, body in (("GET", f"{V2}/entity/guid/{ga['-10']}", None),
                               ("GET", f"{V2}/types/typedef/name/hive_table", None),
                               ("POST", f"{V2}/search/basic", {"typeName": "hive_table", "limit": 10}),
                               ("POST", f"{V2}/entity", {"entity": {"typeName": "hive_db"}})):
        status, resp = target.request(method, path, json=body)
        records.append({"method": method, "path": path, "body": body, "status": status, "response": resp})
    rec = tmp_path / "session.jsonl"
    rec.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    report = replay(list(read_recording(str(rec))), target)
    assert report.passed, [f.as_dict() for f in report.findings]
    assert report.stats["requests skipped (writes / no expectation)"] == 1
    assert report.stats["search requests"] == 1 and report.stats["mean top-10 overlap"] == 1.0

    client.put(f"{V2}/entity/guid/{ga['-10']}", params={"name": "description"}, json="changed")
    report = replay(list(read_recording(str(rec))), target)
    assert [f.item for f in report.findings] == [f"GET {V2}/entity/guid/{ga['-10']}"]


def test_har_and_access_log_readers_and_rewrites(tmp_path):
    har = {"log": {"entries": [
        {"request": {"method": "GET", "url": "https://x/aurelius/atlas/atlas/v2/entity/guid/g1?minExtInfo=true"},
         "response": {"status": 200, "content": {"mimeType": "application/json", "text": "{\"entity\": {}}"}}},
        {"request": {"method": "POST", "url": "https://x/aurelius/atlas/elastic",
                     "postData": {"text": "{\"query\": \"customer\"}"}},
         "response": {"status": 200, "content": {"mimeType": "application/json", "text": "{\"results\": []}"}}},
        {"request": {"method": "GET", "url": "https://x/aurelius/atlas/main.js"},
         "response": {"status": 200, "content": {"mimeType": "application/javascript", "text": "var a"}}}]}}
    p = tmp_path / "s.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    recs = list(read_recording(str(p)))
    assert [r.label for r in recs] == ["GET /aurelius/atlas/atlas/v2/entity/guid/g1?minExtInfo=true",
                                      "POST /aurelius/atlas/elastic"]
    assert recs[1].body == {"query": "customer"}
    assert rewrite(recs[0].path, AURELIUS_REWRITES) == "/api/atlas/v2/entity/guid/g1?minExtInfo=true"
    assert rewrite(recs[1].path, AURELIUS_REWRITES) == "/api/as/v1/engines/atlas-dev/search.json"
    log = tmp_path / "access.log"
    log.write_text('10.0.0.1 - - [28/Sep/2026:10:00:00 +0200] "GET /aurelius/atlas/atlas/v2/types/typedefs HTTP/1.1" '
                   '200 512 "-" "Mozilla"\n'
                   '10.0.0.1 - - [28/Sep/2026:10:00:01 +0200] "GET /aurelius/atlas/main.js HTTP/1.1" 200 9 "-" "-"\n'
                   '10.0.0.1 - - [28/Sep/2026:10:00:02 +0200] "POST /aurelius/atlas/elastic HTTP/1.1" 200 9 "-" "-"\n',
                   encoding="utf-8")
    assert [r.label for r in read_recording(str(log))] == ["GET /aurelius/atlas/atlas/v2/types/typedefs"]
    assert isinstance(recs[0], Recorded)


def test_cli_store_on_a_zip(client, tmp_path, monkeypatch):
    """``python -m parity store`` end to end, with the HTTP client replaced by the in-process adapter."""
    from parity import __main__ as cli
    from tests.helpers import create_sales_model
    create_sales_model(client)
    data = client.post("/api/atlas/admin/export", json={"itemsToExport": [
        {"typeName": "hive_db", "uniqueAttributes": {"qualifiedName": "sales@cl1"}}]}).content
    z = tmp_path / "export.zip"
    z.write_bytes(data)
    monkeypatch.setattr(cli, "_client", lambda args, side: TestClientAdapter(client))
    assert cli.main(["--out-dir", str(tmp_path / "reports"), "store", "--zip", str(z), "--right", "x"]) == 0
    reports = list((tmp_path / "reports").glob("*-store/report.md"))
    assert reports and "PASS" in reports[0].read_text(encoding="utf-8")
    assert zipfile.is_zipfile(z)


# ---------------------------------------------------------------------------------------------- rule grammar
def test_rule_grammar_accepts_the_aurelius_rules_and_rejects_code():
    from parity.rules_check import Call, Combined, RuleSyntaxError, parse
    assert parse("completeness('name')") == Call("completeness", ("name",))
    t = parse("completeness('name') | length('dataEntity', 1)")
    assert isinstance(t, Combined) and t.op == "|" and t.right == Call("length", ("dataEntity", 1))
    assert parse("formatting('FUNC_ORG', r'^[a-zA-Z]+$')").args == ("FUNC_ORG", "^[a-zA-Z]+$")
    assert parse("conditional_value('x', {'a': ['b', -1]})").args == ("x", {"a": ["b", -1]})
    for bad in ("completeness((lambda: ().__class__.__base__.__subclasses__())())",   # passes today's validator
                "completeness([c for c in ().__class__.__mro__])",
                "__import__('os')", "completeness('a').__class__", "Completeness('a')", "completeness(x)",
                "completeness('a') + 1", "completeness(name='a')", "", "completeness('a'"):
        with pytest.raises(RuleSyntaxError):
            parse(bad)


def test_all_rules_shipped_in_the_monorepo_fit_the_grammar(tmp_path):
    from parity import __main__ as cli
    if not os.path.exists(POST_INSTALL):
        pytest.skip("Aurelius data not in the monorepo")
    rc = cli.main(["--out-dir", str(tmp_path), "rules", "--repo-defaults"])
    report = json.loads(next(tmp_path.glob("*-quality-rules/report.json")).read_text(encoding="utf-8"))
    errors = [f["details"][0]["note"] for f in report["findings"]]
    # the only expressions outside the grammar use capitalised names, which today's eval rejects as well
    assert all("rejected by today's validate_function_string as well" in e for e in errors), errors
    assert report["summary"]["checked"] > 1800 and rc == (1 if errors else 0)
