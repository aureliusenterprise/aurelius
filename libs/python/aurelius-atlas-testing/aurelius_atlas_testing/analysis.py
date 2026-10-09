"""Joining the API inventory, the specifications and the tests (ADR 049)."""

from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aurelius_atlas_testing.inventory import ApiItem
from aurelius_atlas_testing.records import TestRecord, TraceabilityFile
from aurelius_atlas_testing.specs import Increment, Rule

Status = Literal["covered", "failing", "uncovered", "gate"]


class TestRef(BaseModel):
    """A test that names an item or a rule.

    Attributes:
        project: The project the test belongs to.
        nodeid: The pytest node id.
        outcome: Its outcome in the run, or ``"not run"``.
    """

    __test__ = False
    model_config = ConfigDict(frozen=True)

    project: str
    nodeid: str
    outcome: str


class ItemTrace(BaseModel):
    """One public API item and the tests that name it.

    Attributes:
        project: The project that owns the item.
        item: The item.
        tests: The tests naming it.
        status: ``covered`` (no named test failed), ``failing`` or ``uncovered``.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    item: ApiItem
    tests: tuple[TestRef, ...]
    status: Status


class RuleTrace(BaseModel):
    """One specification rule and the tests that name it.

    Attributes:
        rule: The rule.
        tests: The tests naming it.
        status: ``covered``, ``failing``, ``uncovered`` or ``gate``.
    """

    model_config = ConfigDict(frozen=True)

    rule: Rule
    tests: tuple[TestRef, ...]
    status: Status


class Problem(BaseModel):
    """A declaration that points at nothing.

    Attributes:
        project: Where the test lives.
        nodeid: The test.
        message: What is wrong.
    """

    model_config = ConfigDict(frozen=True)

    project: str
    nodeid: str
    message: str


class Analysis(BaseModel):
    """The traceability of the whole workspace.

    Attributes:
        increments: The specifications read.
        items: Every public item with its tests.
        rules: Every rule with its tests.
        problems: Declarations naming unknown targets or rules.
    """

    model_config = ConfigDict(frozen=True)

    increments: tuple[Increment, ...] = ()
    items: tuple[ItemTrace, ...] = ()
    rules: tuple[RuleTrace, ...] = ()
    problems: tuple[Problem, ...] = ()

    @property
    def gaps(self) -> list[str]:
        """Return one line per uncovered item, uncovered rule and problem."""
        lines = [
            f"uncovered {trace.item.kind}: {trace.item.target}" for trace in self.items if trace.status == "uncovered"
        ]
        lines += [
            f"uncovered rule: {trace.rule.id} ({trace.rule.increment})"
            for trace in self.rules
            if trace.status == "uncovered"
        ]
        lines += [f"{problem.project}: {problem.nodeid}: {problem.message}" for problem in self.problems]
        return lines


def status_of(tests: Sequence[TestRef]) -> Status:
    """Derive a trace status from the tests that name something.

    Args:
        tests: The naming tests.

    Returns:
        ``uncovered`` without tests, ``failing`` if any failed, else ``covered``.
    """
    if not tests:
        return "uncovered"
    if any(test.outcome == "failed" for test in tests):
        return "failing"
    return "covered"


def names(target: str, item: ApiItem) -> bool:
    """Return whether a ``covers`` target names an item.

    A target names an item when it is the item's path; a class item is also named by
    targets inside it.

    Args:
        target: A declared target.
        item: An inventory item.

    Returns:
        Whether the target counts for the item.
    """
    return target == item.target or (item.kind == "class" and target.startswith(item.target + "."))


def is_known(target: str, items: Sequence[ApiItem]) -> bool:
    """Return whether a target is an item, or a module or class that contains items.

    Args:
        target: A declared target.
        items: The whole inventory.

    Returns:
        Whether the target exists in the inventory.
    """
    return any(item.target == target or item.target.startswith(target + ".") for item in items)


def analyse(
    inventories: Mapping[str, Sequence[ApiItem]],
    traces: Sequence[TraceabilityFile],
    increments: Sequence[Increment],
) -> Analysis:
    """Join inventory, tests and rules into one analysis.

    Args:
        inventories: Public items per project.
        traces: The traceability files of all projects.
        increments: All specifications.

    Returns:
        The analysis.
    """
    all_items = [item for items in inventories.values() for item in items]
    tests: list[tuple[str, TestRecord]] = [(trace.project, record) for trace in traces for record in trace.tests]
    rules = [rule for increment in increments for rule in increment.rules]
    rule_ids = {rule.id for rule in rules}

    def ref(project: str, record: TestRecord) -> TestRef:
        return TestRef(project=project, nodeid=record.nodeid, outcome=record.outcome)

    item_traces = []
    for project, items in inventories.items():
        for item in items:
            naming = tuple(ref(p, r) for p, r in tests if any(names(t, item) for t in r.targets))
            item_traces.append(ItemTrace(project=project, item=item, tests=naming, status=status_of(naming)))

    rule_traces = []
    for rule in rules:
        naming = tuple(ref(p, r) for p, r in tests if rule.id in r.rules)
        status: Status = "gate" if rule.verified_by == "gate" and not naming else status_of(naming)
        rule_traces.append(RuleTrace(rule=rule, tests=naming, status=status))

    problems: list[Problem] = []
    for project, record in tests:
        nodeid = record.nodeid.split("[", 1)[0]  # one problem per test function, not per parameter set
        problems += [
            Problem(project=project, nodeid=nodeid, message=f"covers unknown target {target}")
            for target in record.targets
            if not is_known(target, all_items)
        ]
        problems += [
            Problem(project=project, nodeid=nodeid, message=f"covers unknown rule {rule_id}")
            for rule_id in record.rules
            if rule_id not in rule_ids
        ]

    return Analysis(
        increments=tuple(increments),
        items=tuple(item_traces),
        rules=tuple(rule_traces),
        problems=tuple(dict.fromkeys(problems)),
    )
