import pytest
from aurelius_atlas_parity.compare import Difference, allowance_for, differences, judge, pattern_of
from aurelius_atlas_parity.scenario import Allowance, Request, Step

STEP = Step(
    name="read",
    request=Request(method="GET", path="/x"),
    deviations=(Allowance(path="$.entity.attributes.owner", id="DV-01"), Allowance(path="$..note", id="DV-02")),
)


@pytest.mark.covers("aurelius_atlas_parity.compare.differences", rules=["PAR-05"])
def test__differences_lists_every_change() -> None:
    """Changed, missing and extra members and items are all reported with their path."""
    expected = {"a": 1, "b": [1, 2], "c": {"d": "x"}, "gone": True, "odd key": 1}
    actual = {"a": 2, "b": [1], "c": {"d": "x"}, "new": None, "odd key": 2}

    assert [(d.path, d.expected, d.actual) for d in differences(expected, actual)] == [
        ("$.a", 1, 2),
        ("$.b[1]", 2, None),
        ("$.gone", True, None),
        ("$.new", None, None),
        ("$['odd key']", 1, 2),
    ]
    assert differences({"x": [1]}, {"x": [1, 5]})[0].path == "$.x[1]"
    assert differences(1, 1.0) == [Difference(path="$", expected=1, actual=1.0)]
    assert differences({"same": [1]}, {"same": [1]}) == []


@pytest.mark.covers("aurelius_atlas_parity.compare.Difference.describe")
def test__difference_describe() -> None:
    """Descriptions name the path and both values."""
    assert Difference(path="$.a", expected="x", actual="y").describe() == "$.a: expected 'x', got 'y'"


@pytest.mark.covers("aurelius_atlas_parity.compare.pattern_of", rules=["PAR-05"])
@pytest.mark.parametrize(
    ("allowance", "path", "allowed"),
    [
        ("$.a", "$.a", True),
        ("$.a", "$.a.b[0]", True),
        ("$.a", "$.ab", False),
        ("$.a[*].b", "$.a[3].b", True),
        ("$.a[*].b", "$.a[3].c", False),
        ("$..note", "$.x[0].note", True),
        ("$..note", "$.note", True),
        ("$..note", "$.notes", False),
    ],
)
def test__pattern_of(allowance: str, path: str, allowed: bool) -> None:  # noqa: FBT001
    """Allowances cover their path and everything below it; [*] and ..key generalise."""
    assert bool(pattern_of(allowance).match(path)) is allowed


@pytest.mark.covers("aurelius_atlas_parity.compare.allowance_for", rules=["PAR-05"])
def test__allowance_for() -> None:
    """The first matching allowance is returned, or none."""
    assert allowance_for(Difference(path="$.entity.attributes.owner"), STEP.deviations).id == "DV-01"  # type: ignore[union-attr]
    assert allowance_for(Difference(path="$.entity.guid"), STEP.deviations) is None


@pytest.mark.covers("aurelius_atlas_parity.compare.judge", rules=["PAR-05"])
def test__judge_statuses() -> None:
    """Equal answers match; allowed differences deviate; others, and status codes, mismatch."""
    body = {"entity": {"guid": "<guid-1>", "attributes": {"owner": "a"}}, "x": [{"note": "n"}]}
    owner = {"entity": {"guid": "<guid-1>", "attributes": {"owner": "b"}}, "x": [{"note": "m"}]}
    guid = {"entity": {"guid": "<guid-2>", "attributes": {"owner": "a"}}, "x": [{"note": "n"}]}

    assert judge("s", STEP, "GET /x", (200, body), (200, body)).status == "match"
    deviation = judge("s", STEP, "GET /x", (200, body), (200, owner))
    assert (deviation.status, deviation.deviation) == ("deviation", "DV-01, DV-02")
    mismatch = judge("s", STEP, "GET /x", (200, body), (200, guid))
    assert mismatch.status == "mismatch"
    assert mismatch.detail == "$.entity.guid: expected '<guid-1>', got '<guid-2>'"
    status = judge("s", STEP, "GET /x", (200, body), (404, body))
    assert status.detail == "HTTP status: expected 200, got 404"


@pytest.mark.covers("aurelius_atlas_parity.compare.judge", rules=["PAR-05"])
def test__judge_limits_detail_to_three() -> None:
    """At most three differences are spelled out."""
    result = judge("s", STEP, "GET /x", (200, {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1}), (200, {}))

    assert result.detail.endswith("; and 2 more")
