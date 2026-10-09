"""The ``covers`` marker: what a test proves (ADR 049).

A test declares the functions it exercises on purpose and the specification rules it
checks::

    @pytest.mark.covers("aurelius_atlas_store_es.indices.index_name", rules=["ESI-04"])
    def test__index_name_joins_prefix_and_kind(): ...

A test may carry several ``covers`` markers.
"""

import re
from collections.abc import Iterable, Mapping, Sequence

from pydantic import BaseModel, ConfigDict

COVERS = "covers"
COMPONENT = "component"
RULE_ID_PATTERN = re.compile(r"^[A-Z]{2,6}-\d{2,3}$")
TARGET_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$")

MARKER_HELP = {
    COVERS: "covers(target, rules=None): the function (dotted path) and rule ids this test proves",
    COMPONENT: "component: needs Docker; runs against real infrastructure",
}


class InvalidCoversError(ValueError):
    """A ``covers`` marker is malformed."""


class Coverage(BaseModel):
    """What one test declares it covers.

    Attributes:
        targets: Dotted paths of the functions, methods or classes the test proves.
        rules: Specification rule ids (for example ``ESI-04``) the test checks.
    """

    model_config = ConfigDict(frozen=True)

    targets: tuple[str, ...] = ()
    rules: tuple[str, ...] = ()


def parse_covers(args: Sequence[object], kwargs: Mapping[str, object]) -> Coverage:
    """Validate the arguments of one ``covers`` marker.

    Args:
        args: Positional marker arguments; exactly one dotted target path.
        kwargs: Keyword arguments; only ``rules``, a list of rule ids, is allowed.

    Returns:
        The declared coverage.

    Raises:
        InvalidCoversError: If the target or a rule id is malformed, or unknown
            arguments are given.
    """
    if len(args) != 1 or not isinstance(args[0], str):
        msg = "covers() takes exactly one dotted target path as a string"
        raise InvalidCoversError(msg)
    target = args[0]
    if not TARGET_PATTERN.fullmatch(target):
        msg = f"covers() target {target!r} is not a dotted path like 'package.module.function'"
        raise InvalidCoversError(msg)
    unknown = set(kwargs) - {"rules"}
    if unknown:
        msg = f"covers() got unexpected arguments: {', '.join(sorted(unknown))}"
        raise InvalidCoversError(msg)
    rules = kwargs.get("rules") or []
    if isinstance(rules, str) or not isinstance(rules, Iterable):
        msg = "covers() rules must be a list of rule ids"
        raise InvalidCoversError(msg)
    rule_ids = tuple(str(rule) for rule in rules)
    bad = [rule for rule in rule_ids if not RULE_ID_PATTERN.fullmatch(rule)]
    if bad:
        msg = f"covers() rule ids must look like 'ABC-01': {', '.join(bad)}"
        raise InvalidCoversError(msg)
    return Coverage(targets=(target,), rules=rule_ids)


def merge(coverages: Iterable[Coverage]) -> Coverage:
    """Combine the coverage of several markers on one test, keeping first-seen order.

    Args:
        coverages: Coverage declared by each marker.

    Returns:
        One coverage with the targets and rules of all markers, without duplicates.
    """
    targets: dict[str, None] = {}
    rules: dict[str, None] = {}
    for coverage in coverages:
        targets.update(dict.fromkeys(coverage.targets))
        rules.update(dict.fromkeys(coverage.rules))
    return Coverage(targets=tuple(targets), rules=tuple(rules))
