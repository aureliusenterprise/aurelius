"""The ``parity-results.json`` format read by the workspace test report."""

from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

PARITY_FILENAME = "parity-results.json"
ParityStatus = Literal["match", "deviation", "mismatch", "error", "not recorded"]


class ParityResult(BaseModel):
    """The comparison of one scenario step.

    Attributes:
        scenario: The scenario name.
        step: The step within the scenario.
        endpoint: HTTP method and path template, for example ``GET /api/atlas/v2/types/typedefs``.
        status: ``match``; ``deviation`` (differs only where a recorded deviation allows);
            ``mismatch``; ``error`` (the request could not be made); or ``not recorded``
            (no reference fixture exists yet).
        deviation: The deviation ids that allowed differences, comma-separated.
        detail: A short description of the first differences.
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
    return [ParityRun.model_validate_json(path.read_text(encoding="utf-8")) for path in paths]


def write_parity(path: Path, run: ParityRun) -> None:
    """Write a parity result file, creating parent directories.

    Args:
        path: Where to write.
        run: The results.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
