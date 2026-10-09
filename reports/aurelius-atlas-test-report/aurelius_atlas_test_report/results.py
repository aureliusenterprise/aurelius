"""Reading test results: JUnit XML from pytest and Cobertura XML from coverage.py."""

from collections.abc import Iterator
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree as ET

from pydantic import BaseModel, ConfigDict

SKIP_PARTS = frozenset({".git", ".nx", ".venv", "node_modules", "__pycache__", "dist"})
CaseOutcome = Literal["passed", "failed", "skipped"]


class CaseResult(BaseModel):
    """One test case of a JUnit file.

    Attributes:
        classname: The JUnit class name (pytest: dotted test module, plus class).
        name: The test name, including parameters.
        outcome: ``passed``, ``failed`` (failure or error) or ``skipped``.
        seconds: Duration.
        message: Failure, error or skip message, if any.
    """

    model_config = ConfigDict(frozen=True)

    classname: str
    name: str
    outcome: CaseOutcome
    seconds: float
    message: str = ""


class SuiteResult(BaseModel):
    """All cases of one JUnit file, attributed to a project.

    Attributes:
        project: The project directory, relative to the workspace root.
        file: The JUnit file name (``junit.xml`` or ``e2e-junit.xml``).
        cases: The test cases.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    file: str
    cases: tuple[CaseResult, ...]

    def count(self, outcome: CaseOutcome) -> int:
        """Return how many cases had the given outcome.

        Args:
            outcome: The outcome to count.

        Returns:
            The number of cases.
        """
        return sum(case.outcome == outcome for case in self.cases)

    @property
    def seconds(self) -> float:
        """Return the summed duration of all cases."""
        return sum(case.seconds for case in self.cases)


class ModuleCoverage(BaseModel):
    """Coverage of one source file.

    Attributes:
        filename: The file, as coverage.py names it.
        lines_valid: Measurable lines.
        lines_covered: Executed lines.
        branches_valid: Measurable branch destinations.
        branches_covered: Taken branch destinations.
    """

    model_config = ConfigDict(frozen=True)

    filename: str
    lines_valid: int
    lines_covered: int
    branches_valid: int = 0
    branches_covered: int = 0


class ProjectCoverage(BaseModel):
    """Coverage of one project.

    Attributes:
        project: The project directory, relative to the workspace root.
        modules: Per-file coverage.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    modules: tuple[ModuleCoverage, ...]

    @property
    def line_rate(self) -> float | None:
        """Return the share of covered lines, or ``None`` without measurable lines."""
        valid = sum(module.lines_valid for module in self.modules)
        return sum(module.lines_covered for module in self.modules) / valid if valid else None

    @property
    def branch_rate(self) -> float | None:
        """Return the share of covered branches, or ``None`` without branches."""
        valid = sum(module.branches_valid for module in self.modules)
        return sum(module.branches_covered for module in self.modules) / valid if valid else None


def find_files(root: Path, name: str) -> Iterator[Path]:
    """Yield files with the given name under ``root``, skipping caches and dependencies.

    Args:
        root: The workspace root.
        name: The file name to look for.

    Yields:
        Matching paths, sorted.
    """
    for path in sorted(root.rglob(name)):
        if not SKIP_PARTS.intersection(path.relative_to(root).parts):
            yield path


def parse_junit(path: Path, project: str) -> SuiteResult:
    """Read one pytest JUnit XML file.

    Args:
        path: The file.
        project: The project it belongs to.

    Returns:
        Its test cases.
    """
    cases = []
    for case in ET.parse(path).getroot().iter("testcase"):  # noqa: S314 - our own CI output
        outcome: CaseOutcome = "passed"
        message = ""
        for child in case:
            if child.tag in {"failure", "error"}:
                outcome, message = "failed", child.get("message", "") or (child.text or "").strip()
                break
            if child.tag == "skipped":
                outcome, message = "skipped", child.get("message", "")
        cases.append(
            CaseResult(
                classname=case.get("classname", ""),
                name=case.get("name", ""),
                outcome=outcome,
                seconds=float(case.get("time", "0") or 0),
                message=message[:2000],
            )
        )
    return SuiteResult(project=project, file=path.name, cases=tuple(cases))


def parse_coverage(path: Path, project: str) -> ProjectCoverage:
    """Read one Cobertura XML file written by coverage.py.

    Args:
        path: The file.
        project: The project it belongs to.

    Returns:
        Per-file coverage.
    """
    modules = []
    for cls in ET.parse(path).getroot().iter("class"):  # noqa: S314 - our own CI output
        lines = cls.find("lines")
        line_elements = list(lines.iter("line")) if lines is not None else []
        branches_valid = branches_covered = 0
        for line in line_elements:
            condition = line.get("condition-coverage")  # e.g. "50% (1/2)"
            if condition and "(" in condition:
                covered, valid = condition.split("(", 1)[1].rstrip(")").split("/")
                branches_covered += int(covered)
                branches_valid += int(valid)
        modules.append(
            ModuleCoverage(
                filename=cls.get("filename", ""),
                lines_valid=len(line_elements),
                lines_covered=sum(line.get("hits", "0") != "0" for line in line_elements),
                branches_valid=branches_valid,
                branches_covered=branches_covered,
            )
        )
    return ProjectCoverage(project=project, modules=tuple(modules))
