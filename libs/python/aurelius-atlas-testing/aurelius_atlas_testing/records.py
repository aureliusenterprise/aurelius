"""The traceability file a test run writes, and how to read it back."""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

Outcome = Literal["passed", "failed", "skipped", "not run"]
TRACEABILITY_FILENAME = "traceability.json"


class TestRecord(BaseModel):
    """One collected test and what it declares.

    Attributes:
        nodeid: The pytest node id, relative to the project directory.
        targets: Dotted paths the test covers.
        rules: Rule ids the test checks.
        component: Whether the test needs real infrastructure.
        outcome: The result, or ``"not run"`` when only collected.
    """

    __test__ = False  # not a pytest test class
    model_config = ConfigDict(frozen=True)

    nodeid: str
    targets: tuple[str, ...] = ()
    rules: tuple[str, ...] = ()
    component: bool = False
    outcome: Outcome = "not run"


class TraceabilityFile(BaseModel):
    """Everything one pytest session reports about coverage declarations.

    Attributes:
        project: The project directory, relative to the workspace root.
        tests: One record per collected test.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    tests: tuple[TestRecord, ...] = ()


def write_traceability(path: Path, data: TraceabilityFile) -> None:
    """Write a traceability file as indented JSON, creating parent directories.

    Args:
        path: Where to write.
        data: The content.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.model_dump_json(indent=2) + "\n", encoding="utf-8")


def read_traceability(paths: Iterable[Path]) -> list[TraceabilityFile]:
    """Read traceability files, skipping files that do not exist.

    Args:
        paths: Files to read.

    Returns:
        The parsed files, in the order given.

    Raises:
        ValueError: If a file exists but is not a valid traceability file.
    """
    files = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            files.append(TraceabilityFile.model_validate(json.loads(path.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, ValueError) as error:
            msg = f"{path} is not a valid traceability file: {error}"
            raise ValueError(msg) from error
    return files
