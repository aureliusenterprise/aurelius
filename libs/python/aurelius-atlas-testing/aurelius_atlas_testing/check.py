"""Command line: fail when a public function or a specified rule has no test (ADR 049).

Run from the workspace root::

    uv run python -m aurelius_atlas_testing.check --out reports/aurelius-atlas-test-report/dist/analysis.json

By default every project's tests are *collected* (not run) to read their ``covers``
declarations, so the check is complete and fast. With ``--from-runs`` it reads the
``traceability.json`` files that ``pytest --traceability-out`` wrote during a test run
instead, which also carries outcomes.
"""

import argparse
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from aurelius_atlas_testing.analysis import Analysis, analyse
from aurelius_atlas_testing.inventory import inventory
from aurelius_atlas_testing.records import TRACEABILITY_FILENAME, TraceabilityFile, read_traceability
from aurelius_atlas_testing.specs import load_specifications
from aurelius_atlas_testing.workspace import Project, find_projects, load_config

NO_TESTS_COLLECTED = 5


def collect(root: Path, project: Project) -> TraceabilityFile:
    """Collect a project's tests and return their declarations.

    Args:
        root: The workspace root.
        project: The project.

    Returns:
        The declarations, with outcome ``"not run"``.

    Raises:
        RuntimeError: If collection fails (for example a malformed ``covers`` marker).
    """
    if not project.test_directories:
        return TraceabilityFile(project=project.path)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / TRACEABILITY_FILENAME
        command = [
            sys.executable,
            "-m",
            "pytest",
            *project.test_directories,
            "--collect-only",
            "-q",
            f"--traceability-out={out}",
        ]
        result = subprocess.run(command, cwd=root / project.path, capture_output=True, text=True, check=False)  # noqa: S603
        if result.returncode not in {0, NO_TESTS_COLLECTED}:
            msg = f"collecting tests of {project.path} failed:\n{result.stdout}\n{result.stderr}"
            raise RuntimeError(msg)
        files = read_traceability([out])
    return files[0].model_copy(update={"project": project.path}) if files else TraceabilityFile(project=project.path)


def from_runs(root: Path, project: Project) -> TraceabilityFile:
    """Read the traceability file a test run left in a project directory.

    Args:
        root: The workspace root.
        project: The project.

    Returns:
        The recorded declarations and outcomes, or an empty file if none was written.
    """
    files = read_traceability([root / project.path / TRACEABILITY_FILENAME])
    return files[0].model_copy(update={"project": project.path}) if files else TraceabilityFile(project=project.path)


def run_check(root: Path, *, use_runs: bool = False) -> Analysis:
    """Build the traceability analysis of the workspace.

    Args:
        root: The workspace root.
        use_runs: Read test-run results instead of collecting.

    Returns:
        The analysis.
    """
    config = load_config(root)
    projects = find_projects(root, config)
    inventories = {
        project.path: [item for package in project.packages for item in inventory(root / project.path / package)]
        for project in projects
    }
    traces = [(from_runs if use_runs else collect)(root, project) for project in projects]
    increments = load_specifications(root / config.specifications)
    return analyse(inventories, traces, increments)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check and print the gaps.

    Args:
        argv: Command-line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        ``0`` when every public item and test-verified rule is named by a test, else ``1``.
    """
    parser = argparse.ArgumentParser(prog="python -m aurelius_atlas_testing.check", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="workspace root (default: current directory)")
    parser.add_argument("--out", type=Path, help="write the analysis as JSON to this file")
    parser.add_argument("--from-runs", action="store_true", help="read traceability.json files from test runs")
    args = parser.parse_args(argv)

    analysis = run_check(args.root.resolve(), use_runs=args.from_runs)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(analysis.model_dump_json(indent=2) + "\n", encoding="utf-8")

    covered = sum(trace.status != "uncovered" for trace in analysis.items)
    rules = sum(trace.status != "uncovered" for trace in analysis.rules)
    sys.stdout.write(
        f"functions: {covered}/{len(analysis.items)} named by a test; "
        f"rules: {rules}/{len(analysis.rules)} named by a test or the gate\n"
    )
    for line in analysis.gaps:
        sys.stdout.write(f"  {line}\n")
    return 1 if analysis.gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
