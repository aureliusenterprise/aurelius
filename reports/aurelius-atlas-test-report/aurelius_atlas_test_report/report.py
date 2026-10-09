"""Assembling the workspace test report and rendering it as HTML and Markdown."""

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from aurelius_atlas_testing.analysis import Analysis, ItemTrace, RuleTrace, TestRef, status_of
from aurelius_atlas_testing.check import run_check
from aurelius_atlas_testing.records import TRACEABILITY_FILENAME, read_traceability
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from pydantic import BaseModel, ConfigDict

from aurelius_atlas_test_report.parity import PARITY_FILENAME, ParityRun, read_parity
from aurelius_atlas_test_report.results import (
    ProjectCoverage,
    SuiteResult,
    find_files,
    parse_coverage,
    parse_junit,
)

JUNIT_FILES = ("junit.xml", "e2e-junit.xml")
NOT_MEASURED = "\u2013"  # an en dash, shown where a rate is unknown
COVERAGE_FILE = "coverage.xml"


class Totals(BaseModel):
    """The headline numbers of a report.

    Attributes:
        passed: Passed test cases.
        failed: Failed test cases (failures and errors).
        skipped: Skipped test cases.
        functions: Public functions in the traced projects.
        functions_covered: Functions named by at least one test.
        rules: Specified rules.
        rules_covered: Rules named by a test or verified by the gate.
        line_rate: Line coverage over all projects, if measured.
        branch_rate: Branch coverage over all projects, if measured.
        parity_matches: Parity steps that match or deviate as recorded.
        parity_steps: All parity steps.
    """

    model_config = ConfigDict(frozen=True)

    passed: int
    failed: int
    skipped: int
    functions: int
    functions_covered: int
    rules: int
    rules_covered: int
    line_rate: float | None
    branch_rate: float | None
    parity_matches: int
    parity_steps: int

    @property
    def ok(self) -> bool:
        """Return whether nothing failed and everything is traced."""
        return (
            self.failed == 0
            and self.functions_covered == self.functions
            and self.rules_covered == self.rules
            and self.parity_matches == self.parity_steps
        )


class Report(BaseModel):
    """Everything the report shows.

    Attributes:
        generated: When the report was built (UTC, ``YYYY-MM-DD HH:MM``).
        commit: The commit it describes, if known.
        analysis: Traceability, with outcomes from the test run where available.
        suites: JUnit results per project.
        coverage: Coverage per project.
        parity: Parity runs.
        totals: Headline numbers.
    """

    model_config = ConfigDict(frozen=True)

    generated: str
    commit: str
    analysis: Analysis
    suites: tuple[SuiteResult, ...]
    coverage: tuple[ProjectCoverage, ...]
    parity: tuple[ParityRun, ...]
    totals: Totals


def project_of(root: Path, path: Path) -> str:
    """Return the project directory a result file belongs to (its parent), relative to root.

    Args:
        root: The workspace root.
        path: A result file inside a project directory.

    Returns:
        The project path, POSIX style.
    """
    return path.parent.relative_to(root).as_posix()


def with_outcomes(analysis: Analysis, outcomes: dict[tuple[str, str], str]) -> Analysis:
    """Replace "not run" outcomes in the analysis by the outcomes of the test run.

    Args:
        analysis: An analysis built from collected tests.
        outcomes: Outcome per ``(project, nodeid)`` from the run's traceability files.

    Returns:
        The analysis with run outcomes and statuses recomputed.
    """

    def update(tests: tuple[TestRef, ...]) -> tuple[TestRef, ...]:
        return tuple(
            test.model_copy(update={"outcome": outcomes.get((test.project, test.nodeid), test.outcome)})
            for test in tests
        )

    def item(trace: ItemTrace) -> ItemTrace:
        tests = update(trace.tests)
        return trace.model_copy(update={"tests": tests, "status": status_of(tests)})

    def rule(trace: RuleTrace) -> RuleTrace:
        tests = update(trace.tests)
        status = trace.status if trace.status == "gate" else status_of(tests)
        return trace.model_copy(update={"tests": tests, "status": status})

    return analysis.model_copy(
        update={"items": tuple(map(item, analysis.items)), "rules": tuple(map(rule, analysis.rules))}
    )


def current_commit(root: Path) -> str:
    """Return the commit being reported: ``GITHUB_SHA`` in CI, else ``git rev-parse HEAD``.

    Args:
        root: The workspace root.

    Returns:
        The commit hash, or ``"unknown"``.
    """
    if sha := os.environ.get("GITHUB_SHA"):
        return sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except OSError, subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def rate(covered: int, valid: int) -> float | None:
    """Return ``covered / valid``, or ``None`` when nothing was measurable.

    Args:
        covered: Covered units.
        valid: Measurable units.

    Returns:
        The rate between 0 and 1, or ``None``.
    """
    return covered / valid if valid else None


def build_report(root: Path, analysis: Analysis | None = None) -> Report:
    """Gather all results under the workspace root into a report.

    Args:
        root: The workspace root.
        analysis: A precomputed traceability analysis; computed by collection when omitted.

    Returns:
        The report.
    """
    analysis = analysis if analysis is not None else run_check(root)
    runs = read_traceability(find_files(root, TRACEABILITY_FILENAME))
    outcomes: dict[tuple[str, str], str] = {}
    for path, run in zip(find_files(root, TRACEABILITY_FILENAME), runs, strict=True):
        project = project_of(root, path)
        outcomes.update({(project, test.nodeid): test.outcome for test in run.tests})
    analysis = with_outcomes(analysis, outcomes)

    suites = tuple(parse_junit(path, project_of(root, path)) for name in JUNIT_FILES for path in find_files(root, name))
    coverage = tuple(parse_coverage(path, project_of(root, path)) for path in find_files(root, COVERAGE_FILE))
    parity = tuple(read_parity(find_files(root, PARITY_FILENAME)))
    modules = [module for project in coverage for module in project.modules]
    steps = [result for run in parity for result in run.results]

    totals = Totals(
        passed=sum(suite.count("passed") for suite in suites),
        failed=sum(suite.count("failed") for suite in suites),
        skipped=sum(suite.count("skipped") for suite in suites),
        functions=len(analysis.items),
        functions_covered=sum(trace.status != "uncovered" for trace in analysis.items),
        rules=len(analysis.rules),
        rules_covered=sum(trace.status != "uncovered" for trace in analysis.rules),
        line_rate=rate(sum(m.lines_covered for m in modules), sum(m.lines_valid for m in modules)),
        branch_rate=rate(sum(m.branches_covered for m in modules), sum(m.branches_valid for m in modules)),
        parity_matches=sum(step.status in {"match", "deviation"} for step in steps),
        parity_steps=len(steps),
    )
    return Report(
        generated=datetime.now(UTC).strftime("%Y-%m-%d %H:%M"),
        commit=current_commit(root),
        analysis=analysis,
        suites=suites,
        coverage=coverage,
        parity=parity,
        totals=totals,
    )


def percent(value: float | None) -> str:
    """Format a rate as a percentage with one decimal, or a dash when unknown.

    Args:
        value: A rate between 0 and 1, or ``None``.

    Returns:
        For example ``"97.5%"``, or :data:`NOT_MEASURED` when unknown.
    """
    return NOT_MEASURED if value is None else f"{value * 100:.1f}%"


def environment() -> Environment:
    """Return the Jinja environment with the report templates and filters.

    Returns:
        The environment.
    """
    env = Environment(
        loader=PackageLoader("aurelius_atlas_test_report", "templates"),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["percent"] = percent
    return env


def render_html(report: Report) -> str:
    """Render the full report as a self-contained HTML page.

    Args:
        report: The report.

    Returns:
        The HTML.
    """
    return environment().get_template("report.html.j2").render(report=report)


def render_markdown(report: Report) -> str:
    """Render the headline numbers and problems as Markdown (for the CI job summary).

    Args:
        report: The report.

    Returns:
        The Markdown.
    """
    return environment().get_template("summary.md.j2").render(report=report)


def write_report(report: Report, out: Path) -> list[Path]:
    """Write ``index.html``, ``summary.md`` and ``report.json`` into a directory.

    Args:
        report: The report.
        out: The output directory, created if needed.

    Returns:
        The written files.
    """
    out.mkdir(parents=True, exist_ok=True)
    files = {
        out / "index.html": render_html(report),
        out / "summary.md": render_markdown(report),
        out / "report.json": report.model_dump_json(indent=2) + "\n",
    }
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
    return list(files)
