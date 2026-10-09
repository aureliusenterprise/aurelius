import json
from types import SimpleNamespace
from typing import cast

import pytest
from aurelius_atlas_testing.plugin import outcome_of
from aurelius_atlas_testing.records import Outcome

SAMPLE = """
import pytest

@pytest.mark.covers("pkg.mod.func", rules=["ABC-01"])
@pytest.mark.covers("pkg.mod.other")
def test_passes():
    pass

@pytest.mark.component
def test_fails():
    assert False

@pytest.mark.skip(reason="not today")
@pytest.mark.covers("pkg.mod.func")
def test_skipped():
    pass

@pytest.fixture
def broken():
    raise RuntimeError("setup")

def test_errors_in_setup(broken):
    pass
"""


def _records(pytester: pytest.Pytester) -> dict[str, dict[str, object]]:
    data = json.loads((pytester.path / "out.json").read_text())
    return {record["nodeid"].split("::")[-1]: record for record in data["tests"]}


@pytest.mark.covers("aurelius_atlas_testing.plugin.pytest_addoption", rules=["TRC-02"])
@pytest.mark.covers("aurelius_atlas_testing.plugin.pytest_configure", rules=["TRC-02"])
@pytest.mark.covers("aurelius_atlas_testing.plugin.record_for", rules=["TRC-02"])
@pytest.mark.covers(
    "aurelius_atlas_testing.plugin.TraceabilityRecorder.pytest_collection_modifyitems", rules=["TRC-02"]
)
@pytest.mark.covers("aurelius_atlas_testing.plugin.TraceabilityRecorder.pytest_runtest_logreport", rules=["TRC-03"])
@pytest.mark.covers("aurelius_atlas_testing.plugin.TraceabilityRecorder.pytest_sessionfinish", rules=["TRC-02"])
def test__plugin_writes_declarations_and_outcomes(pytester: pytest.Pytester) -> None:
    """A run with --traceability-out writes each test's declarations and outcome."""
    pytester.makepyfile(test_sample=SAMPLE)

    result = pytester.runpytest(
        "-p",
        "no:playwright",
        "-p",
        "no:cov",
        "-o",
        "asyncio_default_fixture_loop_scope=function",
        "--strict-markers",
        "--traceability-out=out.json",
    )

    result.assert_outcomes(passed=1, failed=1, skipped=1, errors=1)
    records = _records(pytester)
    assert records["test_passes"]["targets"] == ["pkg.mod.func", "pkg.mod.other"]
    assert records["test_passes"]["rules"] == ["ABC-01"]
    assert records["test_passes"]["outcome"] == "passed"
    assert records["test_fails"]["component"] is True
    assert records["test_fails"]["outcome"] == "failed"
    assert records["test_skipped"]["outcome"] == "skipped"
    assert records["test_errors_in_setup"]["outcome"] == "failed"


@pytest.mark.covers("aurelius_atlas_testing.plugin.TraceabilityRecorder.pytest_sessionfinish", rules=["TRC-02"])
def test__plugin_collect_only_records_not_run(pytester: pytest.Pytester) -> None:
    """Collecting without running records every test as not run."""
    pytester.makepyfile(test_sample=SAMPLE)

    pytester.runpytest(
        "-p",
        "no:playwright",
        "-p",
        "no:cov",
        "-o",
        "asyncio_default_fixture_loop_scope=function",
        "--collect-only",
        "--traceability-out=out.json",
    )

    assert {record["outcome"] for record in _records(pytester).values()} == {"not run"}


@pytest.mark.covers("aurelius_atlas_testing.plugin.TraceabilityRecorder.pytest_sessionfinish")
def test__plugin_writes_nothing_without_option(pytester: pytest.Pytester) -> None:
    """Without the option no file is written."""
    pytester.makepyfile(test_sample=SAMPLE)

    pytester.runpytest("-p", "no:playwright", "-p", "no:cov", "-o", "asyncio_default_fixture_loop_scope=function")

    assert not (pytester.path / "out.json").exists()


@pytest.mark.covers("aurelius_atlas_testing.plugin.record_for", rules=["TRC-01"])
def test__plugin_stops_on_malformed_marker(pytester: pytest.Pytester) -> None:
    """A malformed covers marker stops the run with an error naming the test."""
    pytester.makepyfile(
        test_bad="""
import pytest

@pytest.mark.covers("nodots")
def test_bad_marker():
    pass
"""
    )

    result = pytester.runpytest(
        "-p", "no:playwright", "-p", "no:cov", "-o", "asyncio_default_fixture_loop_scope=function"
    )

    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*test_bad.py::test_bad_marker: covers() target 'nodots'*"])


def _report(when: str, outcome: str) -> pytest.TestReport:
    return cast(
        "pytest.TestReport",
        SimpleNamespace(
            when=when, failed=outcome == "failed", skipped=outcome == "skipped", passed=outcome == "passed"
        ),
    )


@pytest.mark.covers("aurelius_atlas_testing.plugin.outcome_of", rules=["TRC-03"])
@pytest.mark.parametrize(
    ("phases", "expected"),
    [
        ([("setup", "passed"), ("call", "passed"), ("teardown", "passed")], "passed"),
        ([("setup", "passed"), ("call", "failed"), ("teardown", "passed")], "failed"),
        ([("setup", "failed")], "failed"),
        ([("setup", "skipped")], "skipped"),
        ([("setup", "passed"), ("call", "passed"), ("teardown", "failed")], "failed"),
        ([("setup", "passed")], "not run"),
    ],
)
def test__outcome_of_folds_phases(phases: list[tuple[str, str]], expected: Outcome) -> None:
    """Phase reports fold into one outcome: any failure fails, a skip skips, a passing call passes."""
    outcome: Outcome = "not run"
    for when, result in phases:
        outcome = outcome_of(_report(when, result), outcome)

    assert outcome == expected
