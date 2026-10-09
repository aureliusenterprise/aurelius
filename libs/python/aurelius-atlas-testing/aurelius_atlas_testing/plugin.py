"""Pytest plugin: registers the ``covers`` and ``component`` markers and records them.

Loaded automatically through the ``pytest11`` entry point. With
``--traceability-out=PATH`` it writes every collected test, its declarations and its
outcome to ``PATH`` (relative to the pytest root directory) at the end of the session.
"""

from pathlib import Path

import pytest

from aurelius_atlas_testing.markers import COMPONENT, COVERS, MARKER_HELP, InvalidCoversError, merge, parse_covers
from aurelius_atlas_testing.records import Outcome, TestRecord, TraceabilityFile, write_traceability


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the ``--traceability-out`` option.

    Args:
        parser: The pytest option parser.
    """
    parser.addoption(
        "--traceability-out",
        default=None,
        help="write the covers declarations and outcomes of this session to this JSON file",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register the markers and the recorder.

    Args:
        config: The pytest configuration.
    """
    for help_text in MARKER_HELP.values():
        config.addinivalue_line("markers", help_text)
    config.pluginmanager.register(TraceabilityRecorder(config), "aurelius-atlas-traceability")


def record_for(item: pytest.Item) -> TestRecord:
    """Build the record of one collected test from its markers.

    Args:
        item: The collected test.

    Returns:
        The test's declarations, with outcome ``"not run"``.

    Raises:
        pytest.UsageError: If a ``covers`` marker is malformed; the message names the test.
    """
    try:
        # iter_markers yields the closest (lowest) decorator first; reverse to source order.
        markers = reversed(list(item.iter_markers(COVERS)))
        coverage = merge(parse_covers(marker.args, marker.kwargs) for marker in markers)
    except InvalidCoversError as error:
        msg = f"{item.nodeid}: {error}"
        raise pytest.UsageError(msg) from error
    return TestRecord(
        nodeid=item.nodeid,
        targets=coverage.targets,
        rules=coverage.rules,
        component=item.get_closest_marker(COMPONENT) is not None,
    )


def outcome_of(report: pytest.TestReport, current: Outcome) -> Outcome:
    """Fold one phase report into a test's overall outcome.

    A failure in any phase fails the test; a skip before the call skips it; a passing
    call passes it unless a later phase fails.

    Args:
        report: The report of one phase (setup, call or teardown).
        current: The outcome so far.

    Returns:
        The outcome after this phase.
    """
    if report.failed:
        return "failed"
    if report.skipped and current == "not run":
        return "skipped"
    if report.when == "call" and report.passed and current == "not run":
        return "passed"
    return current


class TraceabilityRecorder:
    """Collects the declarations and outcomes of one session.

    Args:
        config: The pytest configuration of the session.
    """

    def __init__(self, config: pytest.Config) -> None:
        self._config = config
        self.records: dict[str, TestRecord] = {}

    def pytest_collection_modifyitems(self, items: list[pytest.Item]) -> None:
        """Validate every ``covers`` marker and remember each test's declarations.

        Args:
            items: The collected tests.
        """
        for item in items:
            self.records[item.nodeid] = record_for(item)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Update the outcome of the test the report belongs to.

        Args:
            report: The report of one test phase.
        """
        record = self.records.get(report.nodeid)
        if record is not None:
            self.records[report.nodeid] = record.model_copy(update={"outcome": outcome_of(report, record.outcome)})

    def pytest_sessionfinish(self) -> None:
        """Write the traceability file when ``--traceability-out`` is set."""
        out = self._config.getoption("--traceability-out")
        if not out:
            return
        root = Path(self._config.rootpath)
        path = Path(out) if Path(out).is_absolute() else root / out
        write_traceability(path, TraceabilityFile(project=root.name, tests=tuple(self.records.values())))
