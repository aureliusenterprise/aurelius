import pytest
from aurelius_atlas_testing.analysis import Analysis, TestRef, analyse, is_known, names, status_of
from aurelius_atlas_testing.inventory import ApiItem
from aurelius_atlas_testing.records import TestRecord, TraceabilityFile
from aurelius_atlas_testing.specs import Increment, Rule

FUNC = ApiItem(target="pkg.mod.func", kind="function", path="pkg/mod.py", line=1)
CLS = ApiItem(target="pkg.mod.Model", kind="class", path="pkg/mod.py", line=5)
METHOD = ApiItem(target="pkg.mod.Service.run", kind="method", path="pkg/mod.py", line=9)
SPEC = Increment(
    number="0.9",
    title="t",
    status="in review",
    path="0-9.md",
    rules=(
        Rule(id="ABC-01", text="tested", increment="0.9"),
        Rule(id="ABC-02", text="by gate", increment="0.9", verified_by="gate"),
        Rule(id="ABC-03", text="forgotten", increment="0.9"),
    ),
)


def _ref(outcome: str) -> TestRef:
    return TestRef(project="p", nodeid="t", outcome=outcome)


@pytest.mark.covers("aurelius_atlas_testing.analysis.status_of", rules=["TRC-06"])
@pytest.mark.parametrize(
    ("outcomes", "status"),
    [([], "uncovered"), (["passed"], "covered"), (["not run"], "covered"), (["passed", "failed"], "failing")],
)
def test__status_of(outcomes: list[str], status: str) -> None:
    """No test: uncovered; any failed test: failing; otherwise covered."""
    assert status_of([_ref(outcome) for outcome in outcomes]) == status


@pytest.mark.covers("aurelius_atlas_testing.analysis.names", rules=["TRC-05"])
def test__names_exact_and_inside_class() -> None:
    """Targets name items exactly; class items are also named from inside."""
    assert names("pkg.mod.func", FUNC)
    assert not names("pkg.mod.func.inner", FUNC)
    assert names("pkg.mod.Model._validate", CLS)
    assert not names("pkg.mod.ModelX", CLS)


@pytest.mark.covers("aurelius_atlas_testing.analysis.is_known", rules=["TRC-07"])
def test__is_known_accepts_items_modules_and_classes() -> None:
    """Items, and the modules or classes containing items, are known targets."""
    items = [FUNC, METHOD]

    assert is_known("pkg.mod.func", items)
    assert is_known("pkg.mod.Service", items)
    assert is_known("pkg.mod", items)
    assert not is_known("pkg.mod.gone", items)
    assert not is_known("pkg.mo", items)


@pytest.mark.covers("aurelius_atlas_testing.analysis.analyse", rules=["TRC-05", "TRC-06", "TRC-07"])
@pytest.mark.covers("aurelius_atlas_testing.analysis.Analysis.gaps", rules=["TRC-08"])
def test__analyse_joins_items_tests_and_rules() -> None:
    """Items and rules get their naming tests and status; stray declarations become one problem per test."""
    traces = [
        TraceabilityFile(
            project="libs/p",
            tests=(
                TestRecord(nodeid="t::one", targets=("pkg.mod.func",), rules=("ABC-01",), outcome="passed"),
                TestRecord(nodeid="t::two", targets=("pkg.mod.Service.run",), outcome="failed"),
                TestRecord(nodeid="t::three[a]", targets=("pkg.mod.nothing",), rules=("ZZZ-01",)),
                TestRecord(nodeid="t::three[b]", targets=("pkg.mod.nothing",), rules=("ZZZ-01",)),
            ),
        )
    ]

    analysis = analyse({"libs/p": [FUNC, CLS, METHOD]}, traces, [SPEC])

    assert [(trace.item.target, trace.status) for trace in analysis.items] == [
        ("pkg.mod.func", "covered"),
        ("pkg.mod.Model", "uncovered"),
        ("pkg.mod.Service.run", "failing"),
    ]
    assert [(trace.rule.id, trace.status) for trace in analysis.rules] == [
        ("ABC-01", "covered"),
        ("ABC-02", "gate"),
        ("ABC-03", "uncovered"),
    ]
    assert analysis.gaps == [
        "uncovered class: pkg.mod.Model",
        "uncovered rule: ABC-03 (0.9)",
        "libs/p: t::three: covers unknown target pkg.mod.nothing",
        "libs/p: t::three: covers unknown rule ZZZ-01",
    ]


@pytest.mark.covers("aurelius_atlas_testing.analysis.Analysis.gaps", rules=["TRC-08"])
def test__gaps_empty_when_everything_is_named() -> None:
    """A complete analysis has no gaps."""
    assert Analysis().gaps == []
