"""Build the workspace test report: ``uv run python -m aurelius_atlas_test_report``."""

import argparse
import os
import sys
from pathlib import Path

from aurelius_atlas_testing.analysis import Analysis

from aurelius_atlas_test_report.report import build_report, write_report

parser = argparse.ArgumentParser(prog="python -m aurelius_atlas_test_report", description=__doc__)
parser.add_argument("--root", type=Path, default=Path.cwd(), help="workspace root (default: current directory)")
parser.add_argument("--out", type=Path, default=Path("reports/aurelius-atlas-test-report/dist"))
parser.add_argument("--analysis", type=Path, help="analysis JSON from aurelius_atlas_testing.check (else collected)")
args = parser.parse_args()

root = args.root.resolve()
analysis = (
    Analysis.model_validate_json(args.analysis.read_text()) if args.analysis and args.analysis.is_file() else None
)
report = build_report(root, analysis)
written = write_report(report, args.out if args.out.is_absolute() else root / args.out)

if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write((root / args.out / "summary.md").read_text(encoding="utf-8"))
sys.stdout.write("\n".join(str(path) for path in written) + "\n")
