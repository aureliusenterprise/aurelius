from pathlib import Path

import pytest
from aurelius_atlas_parity.scenario import Request, endpoint, load_scenario, load_scenarios, substitute
from pydantic import ValidationError


@pytest.mark.covers("aurelius_atlas_parity.scenario.load_scenario", rules=["PAR-01"])
@pytest.mark.covers("aurelius_atlas_parity.scenario.load_scenarios", rules=["PAR-01"])
def test__load_scenarios(scenario_dir: Path) -> None:
    """Scenarios are read from YAML with their steps, captures and allowances."""
    (scenario,) = load_scenarios(scenario_dir)

    assert scenario.name == "entity-roundtrip"
    assert [step.name for step in scenario.steps] == ["create", "read"]
    assert scenario.steps[0].capture == {"guid": "$.mutatedEntities.CREATE[0].guid"}
    assert scenario.steps[1].deviations[0].id == "DV-01"
    assert scenario.steps[0].request.json_body["entity"]["typeName"] == "DataSet"


@pytest.mark.covers("aurelius_atlas_parity.scenario.load_scenario", rules=["PAR-01"])
@pytest.mark.covers("aurelius_atlas_parity.scenario.Scenario", rules=["PAR-01"])
@pytest.mark.covers("aurelius_atlas_parity.scenario.Step", rules=["PAR-01"])
@pytest.mark.covers("aurelius_atlas_parity.scenario.Allowance", rules=["PAR-01"])
@pytest.mark.parametrize(
    ("text", "message"),
    [
        (
            "name: other\ndescription: d\nsteps: [{name: a, request: {method: GET, path: /x}}]",
            "must match the file name",
        ),
        ("name: s\ndescription: d\nsteps: []", "at least 1"),
        (
            (
                "name: s\ndescription: d\nsteps: [{name: a, request: {method: GET, path: /x}},"
                " {name: a, request: {method: GET, path: /y}}]"
            ),
            "repeated: a",
        ),
        ("name: s\ndescription: d\nsteps: [{name: a, request: {method: GET, path: x}}]", "should match pattern"),
        ("name: s\ndescription: d\nsteps: [{name: a, request: {method: GET, path: /x}, ignore: [bad]}]", "must start"),
        (
            (
                "name: s\ndescription: d\nsteps: [{name: a, request: {method: GET, path: /x},"
                " deviations: [{path: $.a, id: X-1}]}]"
            ),
            "should match pattern",
        ),
        (
            (
                "name: s\ndescription: d\nsteps: [{name: a, request: {method: GET, path: /x},"
                " deviations: [{path: a.b, id: DV-01}]}]"
            ),
            "must start",
        ),
    ],
    ids=[
        "name-mismatch",
        "no-steps",
        "duplicate-step",
        "relative-path",
        "bad-ignore",
        "bad-deviation-id",
        "bad-allowance-path",
    ],
)
def test__load_scenario_rejects_invalid(tmp_path: Path, text: str, message: str) -> None:
    """Malformed scenarios are refused with a message."""
    path = tmp_path / "s.yaml"
    path.write_text(text)

    with pytest.raises((ValidationError, ValueError), match=message):
        load_scenario(path)


@pytest.mark.covers("aurelius_atlas_parity.scenario.substitute", rules=["PAR-02"])
def test__substitute_everywhere() -> None:
    """Variables are replaced in strings at any depth; other values are kept."""
    value = {"a": "x-${id}", "b": ["${id}", 3, None], "c": {"d": "${id}${id}"}}

    assert substitute(value, {"id": "7"}) == {"a": "x-7", "b": ["7", 3, None], "c": {"d": "77"}}


@pytest.mark.covers("aurelius_atlas_parity.scenario.substitute", rules=["PAR-02"])
def test__substitute_unknown_variable() -> None:
    """An unknown variable is an error."""
    with pytest.raises(KeyError):
        substitute("${nope}", {})


@pytest.mark.covers("aurelius_atlas_parity.scenario.endpoint")
def test__endpoint_shows_template() -> None:
    """Endpoints show the path template, not the substituted value."""
    request = Request(method="GET", path="/api/atlas/v2/entity/guid/${guid}")

    assert endpoint(request) == "GET /api/atlas/v2/entity/guid/{guid}"
