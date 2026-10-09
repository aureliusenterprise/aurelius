from pathlib import Path

import pytest
from aurelius_atlas_test_report.results import (
    ModuleCoverage,
    ProjectCoverage,
    find_files,
    parse_coverage,
    parse_junit,
)


@pytest.mark.covers("aurelius_atlas_test_report.results.find_files", rules=["TRC-10"])
def test__find_files_skips_dependencies(workspace: Path) -> None:
    """Result files inside node_modules, .venv or dist are ignored."""
    assert [p.relative_to(workspace).as_posix() for p in find_files(workspace, "junit.xml")] == [
        "libs/aurelius-atlas-x/junit.xml"
    ]


@pytest.mark.covers("aurelius_atlas_test_report.results.parse_junit", rules=["TRC-10"])
@pytest.mark.covers("aurelius_atlas_test_report.results.SuiteResult.count", rules=["TRC-10"])
@pytest.mark.covers("aurelius_atlas_test_report.results.SuiteResult.seconds", rules=["TRC-10"])
def test__parse_junit_maps_outcomes(workspace: Path) -> None:
    """Failures and errors count as failed; skips as skipped; messages and durations are kept."""
    suite = parse_junit(workspace / "libs/aurelius-atlas-x/junit.xml", "libs/aurelius-atlas-x")

    assert [(case.name, case.outcome) for case in suite.cases] == [
        ("test_ok", "passed"),
        ("test_bad[x]", "failed"),
        ("test_err", "failed"),
        ("test_skip", "skipped"),
    ]
    assert suite.cases[1].message == "assert 1 == 2"
    assert suite.cases[2].message == "setup exploded"
    assert (suite.count("passed"), suite.count("failed"), suite.count("skipped")) == (1, 2, 1)
    assert suite.seconds == pytest.approx(0.85)


@pytest.mark.covers("aurelius_atlas_test_report.results.parse_coverage", rules=["TRC-10"])
def test__parse_coverage_counts_lines_and_branches(workspace: Path) -> None:
    """Lines and branch destinations are counted per file."""
    coverage = parse_coverage(workspace / "libs/aurelius-atlas-x/coverage.xml", "libs/aurelius-atlas-x")

    assert coverage.modules[0] == ModuleCoverage(
        filename="pkg/mod.py", lines_valid=3, lines_covered=2, branches_valid=2, branches_covered=1
    )


@pytest.mark.covers("aurelius_atlas_test_report.results.ProjectCoverage.line_rate", rules=["TRC-10"])
@pytest.mark.covers("aurelius_atlas_test_report.results.ProjectCoverage.branch_rate", rules=["TRC-10"])
def test__project_coverage_rates() -> None:
    """Rates are covered over valid; unknown without measurable units."""
    project = ProjectCoverage(
        project="p",
        modules=(ModuleCoverage(filename="a", lines_valid=4, lines_covered=3, branches_valid=2, branches_covered=1),),
    )

    assert project.line_rate == pytest.approx(0.75)
    assert project.branch_rate == pytest.approx(0.5)
    assert ProjectCoverage(project="p", modules=()).line_rate is None
    assert ProjectCoverage(project="p", modules=()).branch_rate is None
