from pathlib import Path

import pytest
from aurelius_atlas_testing.specs import (
    InvalidSpecificationError,
    Rule,
    load_specifications,
    parse_rules,
    parse_specification,
    split_row,
)

SPEC = """# 0.2 Elasticsearch infrastructure

- **Status:** in review

## Semantics

| Id     | Rule                     |
| ------ | ------------------------ |
| ESI-01 | Defaults reach dev       |
| ESI-02 | Credentials come in pairs |

## Other table

| Name | Value |
| ---- | ----- |
| ESI  | ignored, not a rule id |
"""

GATED = """# 0.1 Adopt

| Id     | Rule            | Verified by |
| ------ | --------------- | ----------- |
| ADO-01 | Tested          |             |
| ADO-02 | Proven by gate  | gate        |
"""


@pytest.mark.covers("aurelius_atlas_testing.specs.split_row")
def test__split_row_strips_cells() -> None:
    """Rows split on pipes into stripped cells."""
    assert split_row("| a | b c |  |") == ["a", "b c", ""]


@pytest.mark.covers("aurelius_atlas_testing.specs.parse_rules", rules=["TRC-09"])
def test__parse_rules_reads_rule_rows_only() -> None:
    """Rows whose first cell is a rule id are rules; other tables are ignored."""
    assert parse_rules(SPEC, "0.2") == [
        Rule(id="ESI-01", text="Defaults reach dev", increment="0.2"),
        Rule(id="ESI-02", text="Credentials come in pairs", increment="0.2"),
    ]


@pytest.mark.covers("aurelius_atlas_testing.specs.parse_rules", rules=["TRC-09"])
def test__parse_rules_reads_verified_by_column() -> None:
    """An empty Verified by means test; gate exempts the rule from needing a test."""
    rules = parse_rules(GATED, "0.1")

    assert [rule.verified_by for rule in rules] == ["test", "gate"]


@pytest.mark.covers("aurelius_atlas_testing.specs.parse_rules", rules=["TRC-09"])
@pytest.mark.parametrize(
    ("text", "message"),
    [
        (GATED.replace("| gate ", "| review"), "must be 'test' or 'gate'"),
        (SPEC.replace("ESI-02", "ESI-01"), "ESI-01 is defined twice"),
    ],
    ids=["unknown-verification", "duplicate-id"],
)
def test__parse_rules_rejects_bad_tables(text: str, message: str) -> None:
    """Unknown verification methods and repeated ids are errors."""
    with pytest.raises(InvalidSpecificationError, match=message):
        parse_rules(text, "0.1")


@pytest.mark.covers("aurelius_atlas_testing.specs.parse_specification", rules=["TRC-09"])
def test__parse_specification(tmp_path: Path) -> None:
    """Number, title, status and rules come from the file."""
    path = tmp_path / "0-2-es.md"
    path.write_text(SPEC)

    increment = parse_specification(path)

    assert (increment.number, increment.title, increment.status, increment.path) == (
        "0.2",
        "Elasticsearch infrastructure",
        "in review",
        "0-2-es.md",
    )
    assert len(increment.rules) == 2


@pytest.mark.covers("aurelius_atlas_testing.specs.parse_specification", rules=["TRC-09"])
def test__parse_specification_requires_numbered_title(tmp_path: Path) -> None:
    """A title without an increment number is refused."""
    path = tmp_path / "x.md"
    path.write_text("# Elasticsearch\n")

    with pytest.raises(InvalidSpecificationError, match="must start with the increment number"):
        parse_specification(path)


@pytest.mark.covers("aurelius_atlas_testing.specs.load_specifications", rules=["TRC-09"])
def test__load_specifications_orders_and_checks_uniqueness(tmp_path: Path) -> None:
    """Specs are ordered numerically, index and template are skipped, and ids are unique across files."""
    (tmp_path / "index.md").write_text("# Increments\n")
    (tmp_path / "template.md").write_text("| ABC-01 | x |\n")
    (tmp_path / "b.md").write_text(SPEC.replace("0.2", "0.10"))
    (tmp_path / "a.md").write_text(GATED)

    assert [increment.number for increment in load_specifications(tmp_path)] == ["0.1", "0.10"]

    (tmp_path / "c.md").write_text(GATED.replace("0.1", "0.3"))
    with pytest.raises(InvalidSpecificationError, match="ADO-01 is defined in both"):
        load_specifications(tmp_path)


@pytest.mark.covers("aurelius_atlas_testing.specs.load_specifications", rules=["TRC-09"])
def test__real_specifications_are_valid(workspace_root: Path) -> None:
    """Every increment specification in this repository follows the format."""
    increments = load_specifications(workspace_root / "docs/architecture/conversion/increments")

    assert [increment.number for increment in increments][:2] == ["0.1", "0.2"]
