from pathlib import Path

import pytest

JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="4">
  <testcase classname="tests.test__a" name="test_ok" time="0.25"/>
  <testcase classname="tests.test__a" name="test_bad[x]" time="0.5">
    <failure message="assert 1 == 2">long trace</failure>
  </testcase>
  <testcase classname="tests.test__a" name="test_err" time="0.1"><error message="">setup exploded</error></testcase>
  <testcase classname="tests.test__a" name="test_skip" time="0"><skipped message="needs docker"/></testcase>
</testsuite></testsuites>
"""

COVERAGE = """<?xml version="1.0" ?>
<coverage version="7"><packages><package name="pkg"><classes>
  <class name="mod.py" filename="pkg/mod.py">
    <lines>
      <line number="1" hits="1"/>
      <line number="2" hits="1" branch="true" condition-coverage="50% (1/2)"/>
      <line number="3" hits="0"/>
    </lines>
  </class>
  <class name="empty.py" filename="pkg/empty.py"><lines/></class>
</classes></package></packages></coverage>
"""

TRACE = """{"project": "aurelius-atlas-x", "tests": [
  {"nodeid": "tests/test__a.py::test_ok", "targets": ["pkg.mod.f"], "rules": ["XYZ-01"], "outcome": "passed"}
]}"""

PARITY = """{"project": "apps/aurelius-atlas-server", "reference": "Apache Atlas 2.4.0", "results": [
  {"scenario": "types", "step": "list", "endpoint": "GET /api/atlas/v2/types/typedefs", "status": "match"},
  {"scenario": "types", "step": "get", "endpoint": "GET /api/atlas/v2/types/typedef/name/{name}", "status": "mismatch",
   "detail": "$.name differs"}
]}"""

ROOT_PYPROJECT = """
[tool.aurelius-atlas.traceability]
projects = ["libs/aurelius-atlas-*"]
specifications = "docs/increments"
"""

SPEC = (
    "# 0.9 Sample\n\n- **Status:** in review\n\n"
    "| Id | Rule |\n| -- | ---- |\n| XYZ-01 | f works |\n| XYZ-02 | g works |\n"
)


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Return a small workspace with one traced project, results and a specification."""
    project = tmp_path / "libs/aurelius-atlas-x"
    (project / "pkg").mkdir(parents=True)
    (project / "pyproject.toml").write_text('[tool.hatch.build.targets.wheel]\npackages = ["pkg"]\n')
    (project / "pkg/__init__.py").write_text("")
    (project / "pkg/mod.py").write_text("def f(): ...\n\n\ndef g(): ...\n")
    (project / "tests").mkdir()
    (project / "tests/test__a.py").write_text(
        'import pytest\n\n\n@pytest.mark.covers("pkg.mod.f", rules=["XYZ-01"])\ndef test_ok():\n    pass\n'
    )
    (project / "junit.xml").write_text(JUNIT)
    (project / "coverage.xml").write_text(COVERAGE)
    (project / "traceability.json").write_text(TRACE)
    (project / "parity-results.json").write_text(PARITY)
    (tmp_path / "node_modules/x").mkdir(parents=True)
    (tmp_path / "node_modules/x/junit.xml").write_text(JUNIT)
    (tmp_path / "docs/increments").mkdir(parents=True)
    (tmp_path / "docs/increments/0-9-sample.md").write_text(SPEC)
    (tmp_path / "pyproject.toml").write_text(ROOT_PYPROJECT)
    return tmp_path
