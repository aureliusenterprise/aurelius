"""Phase 3: governance quality computed by pyatlas, validate_entity, data quality results and the safe rule
evaluator (replacing the update-gov-data-quality Flink job, m4i-validate-entity, the Kafka quality topics and
propagate_quality.py)."""
import json
import os

import pytest

from pyatlas.aurelius import quality_rules as qr
from pyatlas.aurelius.gov_quality import load_rules
from tests.conftest import _fresh_client

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "..", "m4i-atlas-post-install", "data")
ZIP = os.path.join(DATA, "sample_data.zip")
QUALITY = os.path.join(DATA, "atlas-dev-quality.json")
GOV_GOLDEN = os.path.join(DATA, "atlas-dev-gov-quality.json")
V2 = "/api/atlas/v2"
GOV = "/api/aurelius/search/atlas-dev-gov-quality"
sample_only = pytest.mark.skipif(not os.path.exists(ZIP), reason="Aurelius sample data not in the monorepo")


@pytest.fixture(scope="module")
def sample():
    c = _fresh_client(import_on_start=ZIP, import_on_start_mode="always", aurelius_quality_seed=QUALITY)
    flush(c)
    yield c
    c.__exit__(None, None, None)


def flush(c):
    c.portal.call(c.app.state.services.aurelius.flush)


def search(c, engine, **body):
    r = c.post(f"/api/aurelius/search/{engine}", json=body)
    assert r.status_code == 200, r.text
    return [{k: v["raw"] for k, v in x.items() if k != "_meta"} for x in r.json()["results"]]


def gov_docs(c, entity_guid):
    return {d["qualityqualifiedname"]: d for d in search(c, "atlas-dev-gov-quality", page={"size": 100},
                                                          filters={"entity_guid": entity_guid})}


# ------------------------------------------------------------------ rule evaluator
def test_rule_functions_follow_m4i_data_management():
    rows = [{"id": "NL.xxx", "name": "NL.xxx"}, {"id": "NL.xxx", "name": "BE.xxx"}, {"id": "BE.xxx", "name": "BE.xxx"},
            {"id": None, "name": None}, {"id": None, "name": "NL.xxx"}, {"id": "NL.xxx", "name": None}]
    assert list(qr.run("compare_first_characters_starting_without('id', 'name', 2, 'BE')", rows).values()) == \
        [1, 0, 0, 0, 0, 0]
    assert qr.run("completeness('name')", [{"name": "x"}, {"name": None}, {"name": ""}, {}]) == {0: 1, 1: 0, 2: 1, 3: 0}
    assert qr.run("completeness('nope')", [{"name": "x"}]) == {0: 0}                  # missing column: 0
    assert qr.run("length('refs', 1)", [{"refs": []}, {"refs": [{"guid": "g"}]}, {"refs": None}]) == \
        {0: 0, 1: 1, 2: 0}
    assert qr.run("uniqueness('a')", [{"a": 1}, {"a": 1}, {"a": 2}, {"a": None}]) == {0: 0, 1: 0, 2: 1, 3: 1}
    assert qr.run("bijacency('a', 'b')", [{"a": 1, "b": 2}, {"a": 1, "b": 3}, {"a": 4, "b": 5}]) == \
        {0: 0, 1: 0, 2: 1}
    assert qr.run("formatting('c', r'^[a-zA-Z]+$')", [{"c": "abc"}, {"c": "a1"}, {"c": None}]) == {0: 1, 1: 0, 2: 0}
    assert qr.run("range('n', 1, 5)", [{"n": 3}, {"n": 9}, {"n": "x"}]) == {0: 1, 1: 0, 2: 0}
    assert qr.run("validity('v', ['a', 'b'])", [{"v": "a"}, {"v": "c"}]) == {0: 1, 1: 0}
    assert qr.run("invalidity('v', ['a', 'b'])", [{"v": "a"}, {"v": "c"}]) == {0: 0, 1: 1}
    assert qr.run("starts_with('v', 'NL', 'BE')", [{"v": "NL1"}, {"v": "DE1"}, {"v": None}]) == {0: 1, 1: 0, 2: 1}
    assert qr.run("unallowed_text('v', 'Group')", [{"v": "A Group"}, {"v": "B"}]) == {0: 0, 1: 1}
    assert qr.run("contains_character('v', '.', 2)", [{"v": "a.b.c"}, {"v": "a.b"}]) == {0: 1, 1: 0}
    # conditional rules only score the rows that match the condition
    assert qr.run("conditional_completeness('k', 'v', ['x'])", [{"k": "ax", "v": 1}, {"k": "b", "v": None}]) == {0: 1}
    assert qr.run("conditional_value('k', 'v', {'a': ['x', 'y'], 'b': 'z'})",
                  [{"k": "a", "v": "x"}, {"k": "b", "v": "x"}, {"k": "c", "v": 1}]) == {0: 1, 1: 0}
    assert qr.run("new_operating_model_validity('b', 'h', 'f')",
                  [{"b": "Fleet", "h": 1, "f": 2}, {"b": "Other", "h": 1, "f": 2}]) == {0: 0, 1: 1}
    # | = any, & = all
    two = [{"a": "x", "b": None}, {"a": None, "b": None}]
    assert qr.run("completeness('a') | completeness('b')", two) == {0: 1, 1: 0}
    assert qr.run("completeness('a') & completeness('b')", two) == {0: 0, 1: 0}
    assert qr.used_attributes("length('dataDomain', 1) | length('parentEntity', 1)") == ["dataDomain", "parentEntity"]


@pytest.mark.parametrize("expr", [
    "__import__('os').system('id')",
    "completeness((lambda: ().__class__.__base__.__subclasses__())())",   # passed today's validator
    "completeness('a').__class__",
    "completeness(name)",
    "completeness('a') + completeness('b')",
    "completeness(column_name='a')",
    "'x' * 10",
])
def test_rule_expressions_cannot_run_code(expr):
    with pytest.raises(qr.RuleSyntaxError):
        qr.parse(expr)


def test_shipped_rules_load():
    rules = load_rules()
    assert sorted(rules) == ["m4i_collection", "m4i_data_attribute", "m4i_data_domain", "m4i_data_entity",
                             "m4i_dataset", "m4i_field", "m4i_person", "m4i_system"]
    assert sum(len(r) for r in rules.values()) == 27


# ------------------------------------------------------------------ governance quality
@sample_only
def test_gov_quality_matches_the_flink_results(sample):
    """Every document the Flink job produced for the sample, with the same compliance result; the only other
    differences are rule texts that were changed in m4i-governance-data-quality after the golden file was made."""
    ours = {}
    for page in (1, 2):
        ours.update({d["id"]: d for d in search(sample, "atlas-dev-gov-quality",
                                                  page={"size": 1000, "current": page})})
    with open(GOV_GOLDEN, encoding="utf-8") as f:
        golden = {d["id"]: d for d in json.load(f)}
    assert set(ours) == set(golden) and len(ours) == 1628
    rule_fields = {"expression", "name", "noncompliant_message", "dataqualityruledescription"}
    rules = {r["guid"]: r for rs in load_rules().values() for r in rs}
    for doc_id, g in golden.items():
        o = ours[doc_id]
        assert o["compliant"] == g["compliant"], doc_id
        for k in set(o) | set(g):
            if o.get(k) == g.get(k):
                continue
            rule = rules[o["guid"]]
            if k in rule_fields:           # current rule text
                assert o[k] == {"expression": rule["expression"], "name": rule["ruleTitle"],
                                "noncompliant_message": rule["noncompliantMessage"],
                                "dataqualityruledescription": rule["ruleDescription"]}[k]
            elif k == "usedattributes":    # every column of the rule, not only the first
                assert o[k] == qr.used_attributes(rule["expression"])
            else:
                raise AssertionError(f"{doc_id} {k}: {g.get(k)!r} != {o.get(k)!r}")


def test_gov_quality_follows_changes():
    c = _fresh_client()
    try:
        g = c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_domain", "attributes": {
            "qualifiedName": "dq-domain", "name": "DQ domain"}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
        # no flush: an API write answers once the documents are rebuilt (the UI opens the details page next)
        assert c.get("/api/aurelius/search/atlas-dev/documents", params={"ids[]": g}).json()[0]["name"] == "DQ domain"
        docs = gov_docs(c, g)
        assert {k: d["compliant"] for k, d in docs.items()} == {
            "m4i_data_domain--name": "1", "m4i_data_domain--definition": "0",
            "m4i_data_domain--dataEntity": "0", "m4i_data_domain--domainLead": "0"}
        assert docs["m4i_data_domain--definition"]["id"] == f"{g}--{docs['m4i_data_domain--definition']['guid']}"
        # a definition and a data entity make those rules compliant (the entity's side changes the domain too)
        c.put(f"{V2}/entity/guid/{g}", params={"name": "definition"}, json="The domain")
        e = c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_entity", "attributes": {
            "qualifiedName": "dq-entity", "name": "DQ entity"}, "relationshipAttributes": {
            "dataDomain": [{"guid": g, "typeName": "m4i_data_domain"}]}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
        flush(c)
        docs = gov_docs(c, g)
        assert docs["m4i_data_domain--definition"]["compliant"] == "1"
        assert docs["m4i_data_domain--dataEntity"]["compliant"] == "1"
        assert gov_docs(c, e)["m4i_data_entity--dataDomain"]["compliant"] == "1"
        # deleted entities have no governance quality documents
        c.delete(f"{V2}/entity/guid/{e}")
        flush(c)
        assert gov_docs(c, e) == {}
        assert gov_docs(c, g)["m4i_data_domain--dataEntity"]["compliant"] == "0"
    finally:
        c.__exit__(None, None, None)


def test_validate_entity_answers_per_attribute():
    c = _fresh_client()
    try:
        new = {"entity": {"guid": "-1", "typeName": "m4i_data_entity", "attributes": {"name": "E", "definition": None},
                          "relationshipAttributes": {}}, "referredEntities": {}}
        r = c.post("/api/aurelius/validate_entity", json=new)
        assert r.status_code == 200, r.text
        res = r.json()
        assert set(res) == {"name", "definition", "steward", "businessOwner", "dataDomain", "parentEntity",
                            "attributes"}
        assert res["name"]["isNonCompliant"] is False and res["definition"]["isNonCompliant"] is True
        item = res["definition"]["items"][0]
        assert item["compliant"]["raw"] == "0" and item["result"]["raw"] == "This data entity should have a definition"
        assert item["_meta"]["engine"] == "atlas-dev-gov-quality"
        # the either/or rule is shown at both attributes
        assert res["parentEntity"]["items"] == res["dataDomain"]["items"]
        # the editor's raw form value: no type name, the type follows from the form's fields
        form = {"attributes": {"name": "E", "definition": "d", "qualifiedName": None, "typeAlias": None},
                "classifications": [],
                "relationshipAttributes": {"attributes": [], "businessOwner": [], "childEntity": [],
                                           "dataDomain": [{"guid": "x", "typeName": "m4i_data_domain"}],
                                           "parentEntity": [], "steward": []}}
        res = c.post("/api/aurelius/validate_entity", json=form).json()
        assert res["definition"]["isNonCompliant"] is False and res["dataDomain"]["isNonCompliant"] is False
        assert res["steward"]["isNonCompliant"] is True
        person = {"attributes": {"email": None, "name": "P", "qualifiedName": None, "typeAlias": None},
                  "relationshipAttributes": {"businessOwnerAttribute": [], "businessOwnerEntity": [],
                                             "domainLead": [], "stewardAttribute": [], "stewardEntity": []}}
        res = c.post("/api/aurelius/validate_entity", json=person).json()
        assert res["email"]["isNonCompliant"] is True
        # types without rules, unknown forms: nothing to report
        assert c.post("/api/aurelius/validate_entity", json={"typeName": "m4i_generic_process"}).json() == {}
        assert c.post("/api/aurelius/validate_entity", json={"attributes": {"zzz": 1}}).json() == {}
        # the reverse proxy path of the frontend (/aurelius/atlas/validate_entity) needs a login like the rest
        c.auth = None
        assert c.post("/api/aurelius/validate_entity", json=new).status_code == 401
    finally:
        c.__exit__(None, None, None)


# ------------------------------------------------------------------ data quality results
@sample_only
def test_seeded_data_quality_results_take_their_metadata_from_the_rules(sample):
    docs = {d["id"]: d for d in search(sample, "atlas-dev-quality", page={"size": 100})}
    assert len(docs) == 42
    d = docs["nl1--nl1hr--nl1hr001--func_organization--28"]
    e = sample.get(f"{V2}/entity/guid/{d['qualityguid']}").json()["entity"]["attributes"]
    assert (d["expression"], d["dataqualityruledescription"], d["dataqualityruledimension"]) == \
        (e["expression"], e["ruleDescription"], e["qualityDimension"])
    assert (d["dqscore"], d["name"], d["datadomainname"]) == (0.892, "Rule 43", "Personnel and Organization")


@sample_only
def test_posted_data_quality_results_roll_up():
    c = _fresh_client(import_on_start=ZIP, import_on_start_mode="always")
    try:
        flush(c)
        assert search(c, "atlas-dev-quality") == []
        rule_qn = "nl1--nl1hr--nl1hr001--func_organization--28"
        rule = c.get(f"{V2}/entity/uniqueAttribute/type/m4i_data_quality",
                     params={"attr:qualifiedName": rule_qn}).json()["entity"]
        field = rule["relationshipAttributes"]["fields"][0]["guid"]
        r = c.post("/api/aurelius/quality/results", json={"results": [
            {"quality": rule_qn, "dqscore": 0.5, "businessRuleId": 43},
            {"quality": "no-such-rule", "dqscore": 1}]})
        assert r.status_code == 200, r.text
        assert r.json() == {"written": 1, "unknown": ["no-such-rule"]}
        flush(c)
        doc = search(c, "atlas-dev-quality")[0]
        assert (doc["id"], doc["dqscore"], doc["fieldguid"], doc["dataqualityruledimension"], doc["name"]) == \
            (rule_qn, 0.5, field, "Accuracy", "Rule 43")
        assert doc["datadomainname"]            # derived from the field's data attribute
        fdoc = c.get("/api/aurelius/search/atlas-dev/documents", params={"ids[]": field}).json()[0]
        assert (fdoc["dqscore_accuracy"], fdoc["dqscorecnt_accuracy"], fdoc["dqscore_overall"]) == (0.5, 1.0, 0.5)
        up = fdoc["breadcrumbguid"][0]
        assert c.get("/api/aurelius/search/atlas-dev/documents", params={"ids[]": up}).json()[0][
            "dqscorecnt_accuracy"] == 1.0
        # a new run replaces the score; the rule's guid works as reference too
        c.post("/api/aurelius/quality/results", json=[{"quality": rule["guid"], "dqscore": 1}])
        flush(c)
        assert c.get("/api/aurelius/search/atlas-dev/documents", params={"ids[]": field}).json()[0][
            "dqscore_accuracy"] == 1.0
        # validation and permissions
        assert c.post("/api/aurelius/quality/results", json=[{"quality": rule_qn, "dqscore": 2}]).status_code == 400
        assert c.post("/api/aurelius/quality/results", json={"x": 1}).status_code == 400
        c.auth = ("rangertagsync", "rangertagsync")
        assert c.post("/api/aurelius/quality/results", json=[{"quality": rule_qn, "dqscore": 1}]).status_code == 403
        c.auth = ("admin", "admin")
        # deleting the rule entity removes its results; the scores are gone from the field
        c.delete(f"{V2}/entity/guid/{rule['guid']}")
        flush(c)
        assert search(c, "atlas-dev-quality") == []
        assert c.get("/api/aurelius/search/atlas-dev/documents", params={"ids[]": field}).json()[0][
            "dqscorecnt_overall"] == 0.0
        # explicit removal
        other = "nl1--nl1hr--nl1hr001--func_organization--27"
        c.post("/api/aurelius/quality/results", json=[{"quality": other, "dqscore": 1}])
        assert c.delete("/api/aurelius/quality/results").status_code == 400
        assert c.delete("/api/aurelius/quality/results", params={"quality": other}).json() == {"deleted": 1}
        assert c.delete("/api/aurelius/quality/results", params={"all": "true"}).json() == {"deleted": 0}
    finally:
        c.__exit__(None, None, None)
