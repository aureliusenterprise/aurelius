import json
from pathlib import Path

import httpx
import pytest
from aurelius_atlas_parity.normalise import NormalisationRules
from aurelius_atlas_parity.runner import (
    Exchange,
    StepFailedError,
    capture,
    compare,
    fixture_path,
    load_fixture,
    record,
    save_fixture,
    send,
)
from aurelius_atlas_parity.scenario import Request, Step, load_scenarios
from tests.conftest import GUID_A, GUID_C, atlas_like, client_for


@pytest.mark.covers("aurelius_atlas_parity.runner.send", rules=["PAR-02"])
def test__send_substitutes_and_parses() -> None:
    """Variables reach path, query and body; JSON answers are parsed, others kept as text."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/text":
            return httpx.Response(200, text="plain")
        return httpx.Response(201, json={"ok": True})

    step = Step(name="s", request=Request(method="PUT", path="/e/${id}", query={"q": "${id}"}, json={"v": "${id}"}))
    with client_for(handler) as client:
        exchange = send(client, step, {"id": "7"})
        text = send(client, Step(name="t", request=Request(method="GET", path="/text")), {})

    assert exchange == Exchange(status=201, body={"ok": True})
    assert seen[0].url.path == "/e/7"
    assert seen[0].url.params["q"] == "7"
    assert json.loads(seen[0].content) == {"v": "7"}
    assert text.body == "plain"


@pytest.mark.covers("aurelius_atlas_parity.runner.send", rules=["PAR-02", "PAR-07"])
def test__send_failures() -> None:
    """Unknown variables and transport errors become StepFailedError."""

    def broken(request: httpx.Request) -> httpx.Response:
        message = "refused"
        raise httpx.ConnectError(message, request=request)

    with client_for(broken) as client:
        with pytest.raises(StepFailedError, match="unknown variable"):
            send(client, Step(name="s", request=Request(method="GET", path="/${x}")), {})
        with pytest.raises(StepFailedError, match="request failed"):
            send(client, Step(name="s", request=Request(method="GET", path="/x")), {})


@pytest.mark.covers("aurelius_atlas_parity.runner.capture", rules=["PAR-02", "PAR-07"])
def test__capture() -> None:
    """Captured values are stored as strings; a missing value fails the step."""
    step = Step(name="s", request=Request(method="GET", path="/x"), capture={"n": "$.a[0]"})
    variables: dict[str, str] = {}

    capture(step, Exchange(status=200, body={"a": [5]}), variables)

    assert variables == {"n": "5"}
    with pytest.raises(StepFailedError, match="capture n found nothing"):
        capture(step, Exchange(status=200, body={}), variables)


@pytest.mark.covers("aurelius_atlas_parity.runner.record", rules=["PAR-04"])
def test__record_normalises_each_step(scenario_dir: Path, rules: NormalisationRules) -> None:
    """Recording keeps endpoint, status and normalised body per step."""
    (scenario,) = load_scenarios(scenario_dir)

    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "Apache Atlas 2.4.0")

    assert fixture.scenario == "entity-roundtrip"
    assert [step.endpoint for step in fixture.steps] == [
        "POST /api/atlas/v2/entity",
        "GET /api/atlas/v2/entity/guid/{guid}",
    ]
    read = fixture.steps[1].body
    assert read["entity"]["guid"] == "<guid-1>"
    assert "version" not in read["entity"]
    assert read["entity"]["labels"] == ["a", "b"]
    assert read["referredEntities"] == {"<guid-2>": {"guid": "<guid-2>"}}


@pytest.mark.covers("aurelius_atlas_parity.runner.record", rules=["PAR-04"])
def test__record_fails_whole_scenario(scenario_dir: Path, rules: NormalisationRules) -> None:
    """A failing step records nothing."""
    (scenario,) = load_scenarios(scenario_dir)

    with client_for(lambda _: httpx.Response(200, json={})) as client, pytest.raises(StepFailedError):
        record(client, scenario, rules, "ref")


@pytest.mark.covers("aurelius_atlas_parity.runner.compare", rules=["PAR-05"])
def test__compare_match_and_deviation(scenario_dir: Path, rules: NormalisationRules) -> None:
    """A candidate with other GUIDs and label order matches; an allowed owner change deviates."""
    (scenario,) = load_scenarios(scenario_dir)
    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "ref")

    with client_for(atlas_like(guid=GUID_C, labels=("a", "b"))) as client:
        same = compare(client, scenario, fixture, rules)
    with client_for(atlas_like(owner="bob")) as client:
        owner = compare(client, scenario, fixture, rules)

    assert [r.status for r in same] == ["match", "match"]
    assert [(r.status, r.deviation) for r in owner] == [("match", None), ("deviation", "DV-01")]


@pytest.mark.covers("aurelius_atlas_parity.runner.compare", rules=["PAR-05"])
def test__compare_mismatch_on_status(scenario_dir: Path, rules: NormalisationRules) -> None:
    """A different status code is a mismatch."""
    (scenario,) = load_scenarios(scenario_dir)
    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "ref")

    with client_for(atlas_like(status=404)) as client:
        results = compare(client, scenario, fixture, rules)

    assert results[1].status == "mismatch"
    assert results[1].detail.startswith("HTTP status: expected 200, got 404")


@pytest.mark.covers("aurelius_atlas_parity.runner.compare", rules=["PAR-06"])
def test__compare_without_or_with_stale_fixture(scenario_dir: Path, rules: NormalisationRules) -> None:
    """No fixture, or one with other steps, makes every step not recorded."""
    (scenario,) = load_scenarios(scenario_dir)
    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "ref")
        stale = fixture.model_copy(update={"steps": fixture.steps[:1]})

        missing = compare(client, scenario, None, rules)
        outdated = compare(client, scenario, stale, rules)

    assert {r.status for r in missing + outdated} == {"not recorded"}
    assert missing[0].detail == "no fixture"
    assert "re-record" in outdated[0].detail


@pytest.mark.covers("aurelius_atlas_parity.runner.compare", rules=["PAR-07"])
def test__compare_stops_after_error(scenario_dir: Path, rules: NormalisationRules) -> None:
    """A failing step is an error and later steps are not executed."""
    (scenario,) = load_scenarios(scenario_dir)
    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "ref")

    with client_for(lambda _: httpx.Response(500, json={})) as client:
        results = compare(client, scenario, fixture, rules)

    assert [(r.status, r.detail) for r in results][1] == ("error", "not executed")
    assert results[0].status == "error"
    assert "capture guid found nothing" in results[0].detail


@pytest.mark.covers("aurelius_atlas_parity.runner.save_fixture", rules=["PAR-09"])
@pytest.mark.covers("aurelius_atlas_parity.runner.load_fixture", rules=["PAR-09"])
@pytest.mark.covers("aurelius_atlas_parity.runner.fixture_path")
def test__fixture_round_trip(scenario_dir: Path, rules: NormalisationRules, tmp_path: Path) -> None:
    """Fixtures are written key-sorted and indented, and read back equal; missing ones read as None."""
    (scenario,) = load_scenarios(scenario_dir)
    with client_for(atlas_like()) as client:
        fixture = record(client, scenario, rules, "ref")

    path = save_fixture(tmp_path / "fixtures", fixture)

    assert path == fixture_path(tmp_path / "fixtures", scenario)
    text = path.read_text()
    assert text == json.dumps(json.loads(text), indent=2, sort_keys=True) + "\n"
    assert load_fixture(tmp_path / "fixtures", scenario) == fixture
    assert load_fixture(tmp_path / "nowhere", scenario) is None
    assert GUID_A not in text
