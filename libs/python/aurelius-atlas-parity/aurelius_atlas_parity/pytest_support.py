"""Helpers for parity tests: collecting results for the report, and failing usefully."""

import re
from collections.abc import Iterable, Sequence
from pathlib import Path

import pytest

from aurelius_atlas_parity.results import ParityResult, ParityRun, write_parity
from aurelius_atlas_parity.scenario import Scenario

_DEVIATION_ROW = re.compile(r"^\|\s*(DV-\d{2,3})\s*\|", re.MULTILINE)


class ParityLog:
    """Collects the results of every parity test in a session.

    Args:
        project: The project the tests belong to.
        reference: The reference implementation the fixtures came from.
    """

    def __init__(self, project: str, reference: str) -> None:
        self.project = project
        self.reference = reference
        self.results: list[ParityResult] = []

    def add(self, results: Iterable[ParityResult]) -> None:
        """Add the results of one scenario.

        Args:
            results: The step results.
        """
        self.results.extend(results)

    def write(self, path: Path) -> None:
        """Write everything collected as a ``parity-results.json`` file.

        Args:
            path: Where to write.
        """
        write_parity(path, ParityRun(project=self.project, reference=self.reference, results=tuple(self.results)))


def check_results(results: Sequence[ParityResult]) -> None:
    """Fail, skip or pass a parity test from its scenario's results.

    Args:
        results: One scenario's step results.

    Raises:
        pytest.skip.Exception: When the scenario was never recorded.
        AssertionError: When a step mismatches or errors; the message lists them.
    """
    if results and all(result.status == "not recorded" for result in results):
        pytest.skip(f"scenario {results[0].scenario} has no recorded fixture: {results[0].detail}")
    bad = [result for result in results if result.status not in {"match", "deviation"}]
    if bad:
        lines = "\n".join(f"  {r.step} ({r.endpoint}): {r.status}: {r.detail}" for r in bad)
        msg = f"scenario {results[0].scenario} differs from the reference:\n{lines}"
        raise AssertionError(msg)


def deviation_ids(markdown: str) -> set[str]:
    """Return the deviation ids defined in ``deviations.md``.

    Args:
        markdown: The content of the deviations page.

    Returns:
        Ids such as ``DV-01`` found as the first cell of a table row.
    """
    return set(_DEVIATION_ROW.findall(markdown))


def unknown_deviations(scenarios: Iterable[Scenario], known: set[str]) -> list[str]:
    """List allowances that cite a deviation id ``deviations.md`` does not define.

    Args:
        scenarios: The scenarios.
        known: The defined deviation ids.

    Returns:
        One ``scenario/step: id`` entry per unknown id.
    """
    return [
        f"{scenario.name}/{step.name}: {allowance.id}"
        for scenario in scenarios
        for step in scenario.steps
        for allowance in step.deviations
        if allowance.id not in known
    ]
