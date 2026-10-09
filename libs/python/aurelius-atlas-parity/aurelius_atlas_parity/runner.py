"""Running scenarios: recording the reference, and comparing a candidate with the recording."""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from aurelius_atlas_parity.compare import judge
from aurelius_atlas_parity.normalise import GuidMap, NormalisationRules, normalise
from aurelius_atlas_parity.paths import select
from aurelius_atlas_parity.results import ParityResult
from aurelius_atlas_parity.scenario import Scenario, Step, endpoint, substitute


class Exchange(BaseModel):
    """The raw answer to one step.

    Attributes:
        status: The HTTP status code.
        body: The parsed JSON body, or the text when the body is not JSON.
    """

    model_config = ConfigDict(frozen=True)

    status: int
    body: Any = None


class RecordedStep(BaseModel):
    """One step's normalised reference answer.

    Attributes:
        name: The step name.
        endpoint: Method and path template.
        status: The HTTP status code.
        body: The normalised body.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    endpoint: str
    status: int
    body: Any = None


class Fixture(BaseModel):
    """A scenario's recorded reference answers.

    Attributes:
        scenario: The scenario name.
        reference: What was recorded, for example ``Apache Atlas 2.4.0``.
        recorded: When (UTC date).
        steps: One recorded step per scenario step, in order.
    """

    model_config = ConfigDict(frozen=True)

    scenario: str
    reference: str
    recorded: str
    steps: tuple[RecordedStep, ...]


class StepFailedError(RuntimeError):
    """A step could not be executed (request error or missing capture)."""


def send(client: httpx.Client, step: Step, variables: dict[str, str]) -> Exchange:
    """Send one step's request with variables substituted.

    Args:
        client: A client whose base URL and credentials point at the server.
        step: The step.
        variables: Captured values and ``run``.

    Returns:
        The answer.

    Raises:
        StepFailedError: If the request fails or refers to an unknown variable.
    """
    request = step.request
    try:
        response = client.request(
            request.method,
            substitute(request.path, variables),
            params=substitute(request.query, variables),
            json=substitute(request.json_body, variables),
        )
    except KeyError as error:
        msg = f"step {step.name}: unknown variable {error}"
        raise StepFailedError(msg) from error
    except httpx.HTTPError as error:
        msg = f"step {step.name}: request failed: {error}"
        raise StepFailedError(msg) from error
    try:
        body = response.json()
    except ValueError:
        body = response.text or None
    return Exchange(status=response.status_code, body=body)


def capture(step: Step, exchange: Exchange, variables: dict[str, str]) -> None:
    """Store the step's captured values in ``variables``.

    Args:
        step: The step with its ``capture`` paths.
        exchange: Its raw answer.
        variables: Updated in place.

    Raises:
        StepFailedError: If a capture path selects nothing.
    """
    for name, path in step.capture.items():
        values = select(exchange.body, path)
        if not values:
            msg = f"step {step.name}: capture {name} found nothing at {path}"
            raise StepFailedError(msg)
        variables[name] = str(values[0])


def record(client: httpx.Client, scenario: Scenario, rules: NormalisationRules, reference: str) -> Fixture:
    """Run a scenario against the reference and return its normalised answers.

    Args:
        client: A client for the reference server.
        scenario: The scenario.
        rules: Normalisation rules.
        reference: A description of the reference, stored in the fixture.

    Returns:
        The fixture.

    Raises:
        StepFailedError: If any step cannot be executed; nothing is recorded then.
    """
    variables = {"run": uuid.uuid4().hex[:12]}
    guids = GuidMap()
    steps = []
    for step in scenario.steps:
        exchange = send(client, step, variables)
        capture(step, exchange, variables)
        steps.append(
            RecordedStep(
                name=step.name,
                endpoint=endpoint(step.request),
                status=exchange.status,
                body=normalise(exchange.body, rules, step, guids),
            )
        )
    return Fixture(
        scenario=scenario.name,
        reference=reference,
        recorded=datetime.now(UTC).date().isoformat(),
        steps=tuple(steps),
    )


def compare(
    client: httpx.Client, scenario: Scenario, fixture: Fixture | None, rules: NormalisationRules
) -> list[ParityResult]:
    """Run a scenario against the candidate and judge every step against the fixture.

    Args:
        client: A client for the candidate server.
        scenario: The scenario.
        fixture: Its recorded reference answers, or ``None`` if never recorded.
        rules: Normalisation rules.

    Returns:
        One result per step. Without a fixture (or with one recorded for different steps)
        every step is ``not recorded``; after a step fails, it and the remaining steps are
        ``error``.
    """
    if fixture is None or [s.name for s in fixture.steps] != [s.name for s in scenario.steps]:
        detail = "no fixture" if fixture is None else "fixture steps differ from the scenario; re-record it"
        return [
            ParityResult(
                scenario=scenario.name, step=s.name, endpoint=endpoint(s.request), status="not recorded", detail=detail
            )
            for s in scenario.steps
        ]
    variables = {"run": uuid.uuid4().hex[:12]}
    guids = GuidMap()
    results: list[ParityResult] = []
    for step, recorded in zip(scenario.steps, fixture.steps, strict=True):
        if results and results[-1].status == "error":
            results.append(
                ParityResult(
                    scenario=scenario.name,
                    step=step.name,
                    endpoint=recorded.endpoint,
                    status="error",
                    detail="not executed",
                )
            )
            continue
        try:
            exchange = send(client, step, variables)
            capture(step, exchange, variables)
        except StepFailedError as error:
            results.append(
                ParityResult(
                    scenario=scenario.name,
                    step=step.name,
                    endpoint=recorded.endpoint,
                    status="error",
                    detail=str(error),
                )
            )
            continue
        actual = normalise(exchange.body, rules, step, guids)
        results.append(
            judge(scenario.name, step, recorded.endpoint, (recorded.status, recorded.body), (exchange.status, actual))
        )
    return results


def fixture_path(directory: Path, scenario: Scenario) -> Path:
    """Return where a scenario's fixture is stored.

    Args:
        directory: The fixtures directory.
        scenario: The scenario.

    Returns:
        ``<directory>/<scenario name>.json``.
    """
    return directory / f"{scenario.name}.json"


def load_fixture(directory: Path, scenario: Scenario) -> Fixture | None:
    """Read a scenario's fixture, if it was recorded.

    Args:
        directory: The fixtures directory.
        scenario: The scenario.

    Returns:
        The fixture, or ``None``.
    """
    path = fixture_path(directory, scenario)
    return Fixture.model_validate_json(path.read_text(encoding="utf-8")) if path.is_file() else None


def save_fixture(directory: Path, fixture: Fixture) -> Path:
    """Write a fixture as indented, key-sorted JSON so reviews show small diffs.

    Args:
        directory: The fixtures directory.
        fixture: The fixture.

    Returns:
        The written file.
    """
    import json  # noqa: PLC0415 - only needed when recording

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{fixture.scenario}.json"
    path.write_text(json.dumps(fixture.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
