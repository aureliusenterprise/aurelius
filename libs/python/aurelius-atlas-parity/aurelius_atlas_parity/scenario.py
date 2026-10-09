"""Parity scenarios: sequences of HTTP calls whose answers must equal the reference's.

A scenario is a YAML file::

    name: admin-version
    description: The version endpoint answers with the product name and version.
    steps:
      - name: version
        request: {method: GET, path: /api/atlas/admin/version}
      - name: create
        request:
          method: POST
          path: /api/atlas/v2/entity
          json: {entity: {typeName: DataSet, attributes: {qualifiedName: "q-${run}"}}}
        capture: {guid: "$.mutatedEntities.CREATE[0].guid"}
        ignore: ["$.mutatedEntities"]
        deviations:
          - {path: "$.something", id: DV-07}

``${name}`` in paths, query values and bodies is replaced by a captured value, or by
``run`` — a value unique to each execution — so scenarios can be replayed on a dirty server.
"""

import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from aurelius_atlas_parity.paths import parse_path

Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
_VARIABLE = re.compile(r"\$\{([A-Za-z_]\w*)\}")
_DEVIATION_ID = re.compile(r"^DV-\d{2,3}$")


class Request(BaseModel):
    """One HTTP request of a step.

    Attributes:
        method: The HTTP method.
        path: The path, starting with ``/``; may contain ``${variables}``.
        query: Query parameters; values may contain ``${variables}``.
        json_body: A JSON body (``json`` in YAML).
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    method: Method
    path: str = Field(pattern=r"^/")
    query: dict[str, str | list[str]] = Field(default_factory=dict)
    json_body: Any = Field(default=None, alias="json")


class Allowance(BaseModel):
    """A place where a recorded deviation allows the answers to differ.

    Attributes:
        path: Where the difference is allowed.
        id: The deviation id from ``deviations.md``.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    id: str = Field(pattern=_DEVIATION_ID.pattern)

    @field_validator("path")
    @classmethod
    def _valid_path(cls, value: str) -> str:
        parse_path(value)
        return value


class Step(BaseModel):
    """One request and how to judge its answer.

    Attributes:
        name: Unique within the scenario.
        request: What to send.
        capture: Variables to read from the answer, as ``name: path``.
        ignore: Paths removed from both answers before comparing (in addition to the
            global normalisation rules).
        unordered: Paths of lists whose order does not matter.
        deviations: Where recorded deviations allow differences.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    request: Request
    capture: dict[str, str] = Field(default_factory=dict)
    ignore: tuple[str, ...] = ()
    unordered: tuple[str, ...] = ()
    deviations: tuple[Allowance, ...] = ()

    @field_validator("ignore", "unordered")
    @classmethod
    def _valid_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            parse_path(value)
        return values


class Scenario(BaseModel):
    """A named sequence of steps.

    Attributes:
        name: The scenario name; also the fixture file name.
        description: What the scenario proves.
        steps: The steps, run in order.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    description: str
    steps: tuple[Step, ...] = Field(min_length=1)

    @field_validator("steps")
    @classmethod
    def _unique_step_names(cls, steps: tuple[Step, ...]) -> tuple[Step, ...]:
        names = [step.name for step in steps]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            msg = f"step names must be unique, repeated: {', '.join(duplicates)}"
            raise ValueError(msg)
        return steps


def load_scenario(path: Path) -> Scenario:
    """Read a scenario from a YAML file.

    Args:
        path: The file.

    Returns:
        The validated scenario.

    Raises:
        ValueError: If the name in the file does not match the file name.
    """
    scenario = Scenario.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    if scenario.name != path.stem:
        msg = f"{path.name}: scenario name {scenario.name!r} must match the file name"
        raise ValueError(msg)
    return scenario


def load_scenarios(directory: Path) -> list[Scenario]:
    """Read every ``*.yaml`` scenario in a directory, sorted by name.

    Args:
        directory: The scenario directory.

    Returns:
        The scenarios.
    """
    return [load_scenario(path) for path in sorted(directory.glob("*.yaml"))]


def substitute(value: Any, variables: dict[str, str]) -> Any:  # noqa: ANN401 - any JSON value
    """Replace ``${name}`` in every string inside a JSON-like value.

    Args:
        value: A string, list, dict or scalar.
        variables: The known variables.

    Returns:
        A copy with variables replaced.

    Raises:
        KeyError: If a string refers to an unknown variable.
    """
    if isinstance(value, str):
        return _VARIABLE.sub(lambda match: variables[match.group(1)], value)
    if isinstance(value, list):
        return [substitute(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: substitute(item, variables) for key, item in value.items()}
    return value


def endpoint(request: Request) -> str:
    """Return the method and path template of a request, for reporting.

    Args:
        request: The request.

    Returns:
        For example ``"GET /api/atlas/v2/entity/guid/{guid}"``.
    """
    return f"{request.method} {_VARIABLE.sub(lambda match: '{' + match.group(1) + '}', request.path)}"
