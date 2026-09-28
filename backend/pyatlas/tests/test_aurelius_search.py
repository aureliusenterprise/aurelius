"""Aurelius search documents (replacing the Flink jobs) and the App Search compatible search API."""
import json
import os

import pytest

from parity.diff import Rules
from parity.indices import allowlist_for, compare_documents
from tests.conftest import _fresh_client

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "..", "m4i-atlas-post-install", "data")
ZIP = os.path.join(DATA, "sample_data.zip")
QUALITY = os.path.join(DATA, "atlas-dev-quality.json")
GOV = os.path.join(DATA, "atlas-dev-gov-quality.json")
GOLDEN = os.path.join(DATA, "atlas-dev.json")
V2 = "/api/atlas/v2"
S = "/api/aurelius/search"
STALE_RULES = {"3cb9ab0b-050c-40db-9f12-f136045a77a0", "c4d10911-7661-4058-a2df-a25fbed0e093"}
TWO_PARENTS = {"a3d5ab59-783e-4bdb-868d-bfff41181745", "e4cb40df-f287-4ce0-9819-303995c50949"}
pytestmark = pytest.mark.skipif(not os.path.exists(ZIP), reason="Aurelius sample data not in the monorepo")


@pytest.fixture(scope="module")
def sample():
    c = _fresh_client(import_on_start=ZIP, import_on_start_mode="always", aurelius_quality_seed=f"{QUALITY},{GOV}")
    yield c
    c.__exit__(None, None, None)


def flush(c):
    c.portal.call(c.app.state.services.aurelius.flush)


def search(c, engine="atlas-dev", **body):
    r = c.post(f"{S}/{engine}", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_search_documents_match_the_aurelius_golden_documents(sample):
    """The documents pyatlas computes equal the ones the Flink pipeline produced for the sample data, except where
    the Flink output is incomplete (checked below category by category)."""
    status = sample.get(f"/api/aurelius/admin/search/status").json()
    assert status["documents"] == {"atlas-dev": 684, "atlas-dev-gov-quality": 1628, "atlas-dev-quality": 42}
    ours = search(sample, page={"current": 1, "size": 1000})["results"]
    ours = [{k: v["raw"] for k, v in r.items() if k != "_meta"} for r in ours]
    with open(GOLDEN, encoding="utf-8") as f:
        golden = json.load(f)
    report = compare_documents(golden, ours, allowlist_for("atlas-dev"))
    assert report.stats["matched"] == 684
    unexplained = []
    for f in report.findings:
        for d in f.details:
            p, left, right = d["path"], d["left"], d["right"]
            if p.startswith("classificationstext") and left == "<missing>":
                continue                                    # Flink never filled classifications on create
            if p == "definition" and left is None:
                continue                                    # Flink lost some definitions
            if p == "referenceablequalifiedname" and left == f.item:
                continue                                    # Flink used the guid for processes
            if p.startswith(("derivedfield", "derivedprocess")) and left == "<missing>":
                continue                                    # relations Flink missed (ordering races)
            if f.item in STALE_RULES:
                continue                                    # rules changed after the golden file was made
            if f.item in TWO_PARENTS and p.startswith(("breadcrumb", "parentguid")):
                continue                                    # two parent datasets: Flink's pick depended on timing
            unexplained.append((f.item, d))
    assert not unexplained, json.dumps(unexplained, indent=0)[:4000]


def test_app_search_query_filters_facets_and_paging(sample):
    r = search(sample, query="", page={"current": 1, "size": 5},
               filters={"all": [{"typename": ["m4i_data_domain"]}]},
               facets={"typename": {"type": "value", "size": 20}, "sourcetype": [{"type": "value"}]},
               result_fields={"name": {"raw": {}, "snippet": {"size": 20, "fallback": True}}, "guid": {"raw": {}}})
    assert r["meta"]["page"] == {"current": 1, "total_pages": 2, "total_results": 9, "size": 5}
    assert len(r["results"]) == 5 and set(r["results"][0]) == {"name", "guid", "id", "_meta"}
    assert r["facets"]["typename"][0]["data"] == [{"value": "m4i_data_domain", "count": 9}]
    assert r["facets"]["sourcetype"][0]["data"] == [{"value": "Business", "count": 9}]
    # full text, weighted on the name; snippets highlight the match
    r = search(sample, query="Finance", page={"current": 1, "size": 3},
               result_fields={"name": {"raw": {}, "snippet": {"size": 50}}})
    top = r["results"][0]
    assert top["name"]["raw"] == "Finance" and top["name"]["snippet"] == "<em>Finance</em>"
    # none / any / numeric range
    r = search(sample, filters={"all": [{"typename": "m4i_field"}, {"dqscore_overall": {"from": 0.5}}],
                                "none": [{"name": "OEE"}]}, page={"size": 1000})
    assert r["results"] and all(x["typename"]["raw"] == "m4i_field" and x["dqscore_overall"]["raw"] >= 0.5
                                and x["name"]["raw"] != "OEE" for x in r["results"])
    # sorting
    r = search(sample, filters={"typename": "m4i_data_domain"}, sort=[{"name": "desc"}], page={"size": 20})
    names = [x["name"]["raw"] for x in r["results"]]
    assert names == sorted(names, reverse=True)
    # invalid requests get App Search style errors
    bad = sample.post(f"{S}/atlas-dev", json={"sort": {"nope": "asc"}})
    assert bad.status_code == 400 and bad.json()["errors"]
    assert sample.post(f"{S}/no-such-engine", json={}).status_code == 404


def test_quality_engines_and_documents_endpoint(sample):
    r = search(sample, "atlas-dev-gov-quality", filters={"entity_guid": "1cf84182-97b1-4630-b373-8b1d6bbec8ea"},
               facets={"compliant": {"type": "value"}}, page={"size": 100})
    assert r["meta"]["page"]["total_results"] > 0
    assert {f["value"] for f in r["facets"]["compliant"][0]["data"]} <= {"0", "1"}
    r = search(sample, "atlas-dev-quality", query="syntax", page={"size": 5})
    assert r["results"] and r["results"][0]["dataqualityruledescription"]["raw"]
    docs = sample.get(f"{S}/atlas-dev/documents",
                      params=[("ids[]", "d56db187-2627-41a6-8698-f74d4b76227e"), ("ids[]", "missing")]).json()
    assert docs[0]["name"] == "Personnel and Organization" and docs[1] is None


def test_changes_flow_into_the_search_documents():
    c = _fresh_client(import_on_start=ZIP, import_on_start_mode="always")
    try:
        flush(c)
        domain = "d56db187-2627-41a6-8698-f74d4b76227e"
        before = search(c, filters={"breadcrumbguid": domain}, page={"size": 1000})["results"]
        assert before and all(x["breadcrumbname"]["raw"][0] == "Personnel and Organization" for x in before)
        # rename the domain: every document below it gets the new breadcrumb
        e = c.get(f"{V2}/entity/guid/{domain}").json()["entity"]
        c.put(f"{V2}/entity/guid/{domain}", params={"name": "name"}, json="People")
        flush(c)
        after = search(c, filters={"breadcrumbguid": domain}, page={"size": 1000})["results"]
        assert len(after) == len(before) and all(x["breadcrumbname"]["raw"][0] == "People" for x in after)
        assert search(c, query="People", filters={"guid": domain})["results"][0]["name"]["raw"] == "People"
        # a new data entity in the domain gets its document, a deleted one loses it
        g = c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_entity", "attributes": {
            "qualifiedName": "people--new-entity", "name": "New entity"},
            "relationshipAttributes": {"dataDomain": [{"guid": domain, "typeName": "m4i_data_domain"}]}}}) \
            .json()["mutatedEntities"]["CREATE"][0]["guid"]
        flush(c)
        doc = c.get(f"{S}/atlas-dev/documents", params={"ids[]": g}).json()[0]
        assert doc["breadcrumbguid"] == [domain] and doc["deriveddatadomain"] == ["People"]
        dom = c.get(f"{S}/atlas-dev/documents", params={"ids[]": domain}).json()[0]
        assert g in dom["deriveddataentityguid"]
        c.delete(f"{V2}/entity/guid/{g}")
        flush(c)
        assert c.get(f"{S}/atlas-dev/documents", params={"ids[]": g}).json() == [None]
        assert e["attributes"]["name"] == "Personnel and Organization"
    finally:
        c.__exit__(None, None, None)


def test_rebuild_needs_admin(sample):
    sample.auth = ("rangertagsync", "rangertagsync")
    try:
        r = sample.post(f"/api/aurelius/admin/search/rebuild")
        assert r.status_code == 403
    finally:
        sample.auth = ("admin", "admin")
    assert sample.post(f"/api/aurelius/admin/search/rebuild").json()["documents"] == 684
    assert isinstance(Rules(), Rules)
