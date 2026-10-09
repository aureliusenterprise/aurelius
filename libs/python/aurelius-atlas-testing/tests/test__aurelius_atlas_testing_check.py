from pathlib import Path

import pytest
from aurelius_atlas_testing.check import collect, from_runs, main, run_check
from aurelius_atlas_testing.records import TestRecord, TraceabilityFile, write_traceability
from aurelius_atlas_testing.workspace import Project

ROOT = """
[tool.aurelius-atlas.traceability]
projects = ["libs/aurelius-atlas-*"]
specifications = "docs/increments"
"""
SPEC = "# 0.9 Sample\n\n| Id | Rule |\n| -- | ---- |\n| SMP-01 | add adds |\n"
CODE = "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n"
TEST = """
import pytest
from sample import add

@pytest.mark.covers("sample.add", rules=["SMP-01"])
def test_add():
    assert add(1, 2) == 3
"""


def _workspace(tmp_path: Path, *, cover_sub: bool) -> Path:
    project = tmp_path / "libs/aurelius-atlas-sample"
    (project / "sample").mkdir(parents=True)
    (project / "tests").mkdir()
    (tmp_path / "docs/increments").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(ROOT)
    (tmp_path / "docs/increments/0-9-sample.md").write_text(SPEC)
    (project / "pyproject.toml").write_text(
        '[tool.hatch.build.targets.wheel]\npackages = ["sample"]\n[tool.pytest.ini_options]\npythonpath = ["."]\n'
    )
    (project / "sample/__init__.py").write_text(CODE)
    test = TEST + ('\n@pytest.mark.covers("sample.sub")\ndef test_sub():\n    pass\n' if cover_sub else "")
    (project / "tests/test_sample.py").write_text(test)
    return tmp_path


@pytest.mark.covers("aurelius_atlas_testing.check.collect", rules=["TRC-08"])
def test__collect_reads_declarations_without_running(tmp_path: Path) -> None:
    """Collection returns each test's declarations, not run."""
    root = _workspace(tmp_path, cover_sub=False)
    project = Project(path="libs/aurelius-atlas-sample", packages=("sample",), test_directories=("tests",))

    trace = collect(root, project)

    assert trace.project == "libs/aurelius-atlas-sample"
    assert [(t.targets, t.rules, t.outcome) for t in trace.tests] == [(("sample.add",), ("SMP-01",), "not run")]


@pytest.mark.covers("aurelius_atlas_testing.check.collect")
def test__collect_without_test_directories_is_empty(tmp_path: Path) -> None:
    """A project without tests yields an empty file."""
    assert collect(tmp_path, Project(path="x", packages=("x",), test_directories=())).tests == ()


@pytest.mark.covers("aurelius_atlas_testing.check.collect", rules=["TRC-01"])
def test__collect_fails_on_malformed_marker(tmp_path: Path) -> None:
    """A collection error (such as a malformed marker) fails the check with pytest's output."""
    root = _workspace(tmp_path, cover_sub=False)
    (root / "libs/aurelius-atlas-sample/tests/test_bad.py").write_text(
        "import pytest\n@pytest.mark.covers('bad')\ndef test_x(): pass\n"
    )
    project = Project(path="libs/aurelius-atlas-sample", packages=("sample",), test_directories=("tests",))

    with pytest.raises(RuntimeError, match="collecting tests of libs/aurelius-atlas-sample failed"):
        collect(root, project)


@pytest.mark.covers("aurelius_atlas_testing.check.from_runs")
def test__from_runs_reads_left_over_file(tmp_path: Path) -> None:
    """Results a test run wrote into the project directory are read back."""
    project = Project(path="p", packages=("p",), test_directories=("tests",))
    record = TestRecord(nodeid="t", targets=("p.f",), outcome="passed")
    write_traceability(tmp_path / "p/traceability.json", TraceabilityFile(project="other", tests=(record,)))

    assert from_runs(tmp_path, project) == TraceabilityFile(project="p", tests=(record,))
    assert from_runs(tmp_path, Project(path="q", packages=("q",), test_directories=())).tests == ()


@pytest.mark.covers("aurelius_atlas_testing.check.run_check", rules=["TRC-08"])
def test__run_check_finds_uncovered_function(tmp_path: Path) -> None:
    """A public function no test names is a gap; the covered one and its rule are not."""
    analysis = run_check(_workspace(tmp_path, cover_sub=False))

    assert analysis.gaps == ["uncovered function: sample.sub"]


@pytest.mark.covers("aurelius_atlas_testing.check.main", rules=["TRC-08"])
def test__main_exit_codes_and_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 1 with the gaps listed when something is uncovered, 0 when complete; JSON written on request."""
    root = _workspace(tmp_path, cover_sub=False)

    assert main(["--root", str(root)]) == 1
    assert "uncovered function: sample.sub" in capsys.readouterr().out

    root = _workspace(tmp_path / "complete", cover_sub=True)
    out = tmp_path / "analysis.json"
    assert main(["--root", str(root), "--out", str(out)]) == 0
    assert "functions: 2/2 named by a test; rules: 1/1" in capsys.readouterr().out
    assert '"status": "covered"' in out.read_text()


@pytest.mark.covers("aurelius_atlas_testing.check.main", rules=["TRC-08"])
def test__main_from_runs(tmp_path: Path) -> None:
    """With --from-runs nothing is collected; missing run files leave everything uncovered."""
    assert main(["--root", str(_workspace(tmp_path, cover_sub=True)), "--from-runs"]) == 1
