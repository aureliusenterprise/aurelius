"""Parity results: how the new system's answers compare with the reference (ADR 048).

The parity harness (increment 0.4) writes one ``parity-results.json`` per test run. This
module defines that format so the report can show it.
"""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

PARITY_FILENAME = "parity-results.json"
ParityStatus = Literal["match", "deviation", "mismatch", "error"]


class ParityResult(BaseModel):
    """The comparison of one scenario step.

    Attributes:
        scenario: The scenario name.
        step: The step within the scenario.
        endpoint: HTTP method and path template, for example ``GET /api/atlas/v2/types/typedefs``.
        status: ``match``; ``deviation`` (differs as a recorded deviation allows);
            ``mismatch``; or ``error`` (the request could not be made).
        deviation: The deviation id that allowed a difference, if any.
        detail: A short description of the first difference.
    """

    model_config = ConfigDict(frozen=True)

    scenario: str
    step: str
    endpoint: str
    status: ParityStatus
    deviation: str | None = None
    detail: str = ""


class ParityRun(BaseModel):
    """All parity results of one run.

    Attributes:
        project: The project whose tests produced them.
        reference: The reference implementation, for example ``Apache Atlas 2.4.0``.
        results: One result per scenario step.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    reference: str
    results: tuple[ParityResult, ...] = ()


def read_parity(paths: Iterable[Path]) -> list[ParityRun]:
    """Read parity result files.

    Args:
        paths: The files.

    Returns:
        The runs, in the order given.
    """
    return [ParityRun.model_validate(json.loads(path.read_text(encoding="utf-8"))) for path in paths]
