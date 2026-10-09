"""Command line for recording parity fixtures from the reference Atlas."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from aurelius_atlas_parity.normalise import load_rules
from aurelius_atlas_parity.runner import StepFailedError, record, save_fixture
from aurelius_atlas_parity.scenario import load_scenarios

DEFAULT_REFERENCE = "Apache Atlas 2.4.0"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser.

    Returns:
        The parser with the ``record`` command.
    """
    parser = argparse.ArgumentParser(prog="python -m aurelius_atlas_parity")
    commands = parser.add_subparsers(dest="command", required=True)
    rec = commands.add_parser("record", help="record fixtures from the reference server")
    rec.add_argument("--base-url", default="http://localhost:21000")
    rec.add_argument("--user", default="admin")
    rec.add_argument("--password", default="atlasR0cks!")
    rec.add_argument("--scenarios", type=Path, required=True, help="directory of *.yaml scenarios")
    rec.add_argument("--fixtures", type=Path, required=True, help="directory to write fixtures to")
    rec.add_argument("--rules", type=Path, required=True, help="normalisation rules YAML")
    rec.add_argument("--reference", default=DEFAULT_REFERENCE, help="description stored in each fixture")
    rec.add_argument("--only", nargs="*", default=None, help="record only these scenario names")
    return parser


def main(argv: Sequence[str] | None = None, client: httpx.Client | None = None) -> int:
    """Record the selected scenarios.

    Args:
        argv: Arguments; defaults to ``sys.argv[1:]``.
        client: A client to use instead of one built from the arguments (for tests).

    Returns:
        ``0`` when every selected scenario was recorded, ``1`` otherwise.
    """
    args = build_parser().parse_args(argv)
    rules = load_rules(args.rules)
    scenarios = [s for s in load_scenarios(args.scenarios) if args.only is None or s.name in args.only]
    http = client or httpx.Client(base_url=args.base_url, auth=(args.user, args.password), timeout=60.0)
    failed = 0
    with http:
        for scenario in scenarios:
            try:
                path = save_fixture(args.fixtures, record(http, scenario, rules, args.reference))
            except StepFailedError as error:
                failed += 1
                sys.stderr.write(f"{scenario.name}: not recorded: {error}\n")
                continue
            sys.stdout.write(f"{scenario.name}: recorded {path}\n")
    return 1 if failed else 0
