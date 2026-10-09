import json
from pathlib import Path

import pytest
from aurelius_atlas_test_report.parity import read_parity
from aurelius_atlas_test_report.report import (
    NOT_MEASURED,
    Totals,
    build_report,
    current_commit,
    environment,
    percent,
    project_of,
    rate,
    render_html,
    render_markdown,
    with_outcomes,
    write_report,
)
from aurelius_atlas_testing.analysis import Analysis, ItemTrace, RuleTrace, TestRef
from aurelius_atlas_testing.inventory import ApiItem
from aurelius_atlas_testing.specs import Rule


@pytest.mark.covers("aurelius_atlas_parity.results.read_parity", rules=["TRC-10"])
def test__read_parity(workspace: Path) -> None:
    """Parity files are read with their per-step status."""
    (run,) = read_parity([workspace / "libs/aurelius-atlas-x/parity-results.json"])

    assert run.reference == "Apache Atlas 2.4.0"
    assert [result.status for result in run.results] == ["match", "mismatch"]


@pytest.mark.covers("aurelius_atlas_test_report.report.project_of")
def test__project_of(tmp_path: Path) -> None:
    """A result file belongs to the directory it sits in."""
    assert project_of(tmp_path, tmp_path / "libs/a/junit.xml") == "libs/a"


@pytest.mark.covers("aurelius_atlas_test_report.report.rate")
@pytest.mark.covers("aurelius_atlas_test_report.report.percent", rules=["TRC-10"])
def test__rate_and_percent() -> None:
    """Rates format with one decimal; unknown rates show a dash."""
    assert rate(1, 4) == pytest.approx(0.25)
    assert rate(0, 0) is None
    assert percent(0.975) == "97.5%"
    assert percent(None) == NOT_MEASURED


@pytest.mark.covers("aurelius_atlas_test_report.report.with_outcomes", rules=["TRC-06", "TRC-10"])
def test__with_outcomes_recomputes_status() -> None:
    """Run outcomes replace 'not run' and statuses follow; gate rules stay gate."""
    item = ApiItem(target="p.f", kind="function", path="p.py", line=1)
    ref = TestRef(project="libs/p", nodeid="t::a", outcome="not run")
    analysis = Analysis(
        items=(ItemTrace(project="libs/p", item=item, tests=(ref,), status="covered"),),
        rules=(
            RuleTrace(rule=Rule(id="A-01", text="", increment="0.1"), tests=(ref,), status="covered"),
            RuleTrace(rule=Rule(id="A-02", text="", increment="0.1", verified_by="gate"), tests=(), status="gate"),
        ),
    )

    updated = with_outcomes(analysis, {("libs/p", "t::a"): "failed"})

    assert updated.items[0].status == "failing"
    assert updated.items[0].tests[0].outcome == "failed"
    assert [trace.status for trace in updated.rules] == ["failing", "gate"]


@pytest.mark.covers("aurelius_atlas_test_report.report.current_commit")
def test__current_commit_prefers_ci_variable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GITHUB_SHA wins; outside a git repository the commit is unknown."""
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    assert current_commit(tmp_path) == "abc123"

    monkeypatch.delenv("GITHUB_SHA")
    assert current_commit(tmp_path) == "unknown"


@pytest.mark.covers("aurelius_atlas_test_report.report.build_report", rules=["TRC-10"])
@pytest.mark.covers("aurelius_atlas_test_report.report.Totals.ok", rules=["TRC-10"])
def test__build_report_joins_everything(workspace: Path) -> None:
    """Results, coverage, parity and traceability (with run outcomes) end up in one report."""
    report = build_report(workspace)
    totals = report.totals

    assert (totals.passed, totals.failed, totals.skipped) == (1, 2, 1)
    assert (totals.functions_covered, totals.functions) == (1, 2)
    assert (totals.rules_covered, totals.rules) == (1, 2)
    assert (totals.parity_matches, totals.parity_steps) == (1, 2)
    assert totals.line_rate == pytest.approx(2 / 3)
    assert not totals.ok
    assert report.analysis.items[0].tests[0].outcome == "passed"


@pytest.mark.covers("aurelius_atlas_test_report.report.Totals.ok", rules=["TRC-10"])
def test__totals_ok_only_when_everything_holds() -> None:
    """A report is ok only with no failures, full traceability and full parity."""
    base = {
        "passed": 3,
        "failed": 0,
        "skipped": 1,
        "functions": 2,
        "functions_covered": 2,
        "rules": 1,
        "rules_covered": 1,
        "line_rate": None,
        "branch_rate": None,
        "parity_matches": 0,
        "parity_steps": 0,
    }

    assert Totals.model_validate(base).ok
    assert not Totals.model_validate({**base, "failed": 1}).ok
    assert not Totals.model_validate({**base, "rules_covered": 0}).ok


@pytest.mark.covers("aurelius_atlas_test_report.report.environment")
@pytest.mark.covers("aurelius_atlas_test_report.report.render_html", rules=["TRC-10"])
@pytest.mark.covers("aurelius_atlas_test_report.report.render_markdown", rules=["TRC-10"])
def test__render_shows_problems(workspace: Path) -> None:
    """The page and the summary name failing tests, untested functions and rules, and parity differences."""
    report = build_report(workspace)

    html = render_html(report)
    markdown = render_markdown(report)

    assert "2 failing tests" in html
    assert "1 untested function." in html
    assert "XYZ-02" in html
    assert "$.name differs" in html
    assert "<script" not in html
    assert environment().autoescape
    assert "| 1 passed, 2 failed, 1 skipped | 1 / 2 | 1 / 2 |" in markdown
    assert "uncovered function: pkg.mod.g" in markdown
    assert "test__a::test_bad[x]" in markdown


@pytest.mark.covers("aurelius_atlas_test_report.report.render_html", rules=["TRC-10"])
def test__render_without_results(workspace: Path) -> None:
    """Without any results the page still renders, saying so."""
    for name in ("junit.xml", "coverage.xml", "traceability.json", "parity-results.json"):
        (workspace / "libs/aurelius-atlas-x" / name).unlink()

    html = render_html(build_report(workspace))

    assert "No JUnit results found" in html
    assert "No parity results in this run." in html
    assert "No coverage results found." in html


@pytest.mark.covers("aurelius_atlas_test_report.report.write_report", rules=["TRC-10"])
def test__write_report_creates_three_files(workspace: Path, tmp_path: Path) -> None:
    """index.html, summary.md and report.json are written; the JSON parses."""
    out = tmp_path / "out"

    written = write_report(build_report(workspace), out)

    assert sorted(path.name for path in written) == ["index.html", "report.json", "summary.md"]
    assert json.loads((out / "report.json").read_text())["totals"]["failed"] == 2
