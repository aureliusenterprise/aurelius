"""Rules stated in increment specifications (ADR 051).

A specification is a Markdown file whose title starts with the increment number
(``# 0.2 Elasticsearch infrastructure``) and whose *Semantics* table lists one rule per
row: ``| ESI-04 | Every index name is <prefix>-<kind> |``. An optional third column
*Verified by* names how a rule is checked when no test can name it; the only accepted
value is ``gate`` (the lint, type-check and test gate itself proves it).
"""

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aurelius_atlas_testing.markers import RULE_ID_PATTERN

VerifiedBy = Literal["test", "gate"]
_TITLE = re.compile(r"^#\s+(\d+\.\d+)\s+(.+?)\s*$", re.MULTILINE)
_STATUS = re.compile(r"^-\s+\*\*Status:\*\*\s+(.+?)\s*$", re.MULTILINE)
_SKIPPED_FILES = {"index.md", "template.md"}


class Rule(BaseModel):
    """One rule of an increment's semantics.

    Attributes:
        id: The rule id, for example ``ESI-04``.
        text: The rule in plain words.
        increment: The increment number, for example ``0.2``.
        verified_by: ``test`` (a ``covers`` test must name it) or ``gate``.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    text: str
    increment: str
    verified_by: VerifiedBy = "test"


class Increment(BaseModel):
    """One increment specification.

    Attributes:
        number: The increment number, for example ``0.2``.
        title: The title after the number.
        status: The status line value, for example ``in review``.
        path: The file name of the specification.
        rules: Its rules in table order.
    """

    model_config = ConfigDict(frozen=True)

    number: str
    title: str
    status: str
    path: str
    rules: tuple[Rule, ...] = ()


class InvalidSpecificationError(ValueError):
    """A specification file does not follow the template."""


def split_row(line: str) -> list[str]:
    """Split a Markdown table row into stripped cells.

    Args:
        line: A line starting and ending with ``|``.

    Returns:
        The cell texts.
    """
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_rules(text: str, increment: str) -> list[Rule]:
    """Read every rule row of every table in a specification.

    Args:
        text: The specification's Markdown.
        increment: The increment number the rules belong to.

    Returns:
        Rules in document order.

    Raises:
        InvalidSpecificationError: If a rule id repeats or *Verified by* has an unknown value.
    """
    rules: list[Rule] = []
    verified_column: int | None = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            verified_column = None
            continue
        cells = split_row(line)
        lowered = [cell.lower() for cell in cells]
        if lowered and lowered[0] == "id":
            verified_column = lowered.index("verified by") if "verified by" in lowered else None
            continue
        if not cells or not RULE_ID_PATTERN.fullmatch(cells[0]):
            continue
        verified = "test"
        if verified_column is not None and verified_column < len(cells) and cells[verified_column]:
            verified = cells[verified_column].lower()
        if verified not in {"test", "gate"}:
            msg = f"rule {cells[0]}: 'Verified by' must be 'test' or 'gate', not {verified!r}"
            raise InvalidSpecificationError(msg)
        if any(rule.id == cells[0] for rule in rules):
            msg = f"rule {cells[0]} is defined twice"
            raise InvalidSpecificationError(msg)
        rules.append(
            Rule(id=cells[0], text=cells[1] if len(cells) > 1 else "", increment=increment, verified_by=verified)  # pyright: ignore[reportArgumentType]
        )
    return rules


def parse_specification(path: Path) -> Increment:
    """Read one increment specification.

    Args:
        path: The Markdown file.

    Returns:
        The increment with its rules.

    Raises:
        InvalidSpecificationError: If the title does not start with an increment number.
    """
    text = path.read_text(encoding="utf-8")
    title = _TITLE.search(text)
    if title is None:
        msg = f"{path.name}: the title must start with the increment number, like '# 0.2 Title'"
        raise InvalidSpecificationError(msg)
    status = _STATUS.search(text)
    number = title.group(1)
    return Increment(
        number=number,
        title=title.group(2),
        status=status.group(1) if status else "unknown",
        path=path.name,
        rules=tuple(parse_rules(text, number)),
    )


def load_specifications(directory: Path) -> list[Increment]:
    """Read every specification in a directory, ordered by increment number.

    Args:
        directory: The increments directory.

    Returns:
        The increments; ``index.md`` and ``template.md`` are skipped.

    Raises:
        InvalidSpecificationError: If two increments define the same rule id.
    """
    increments = [
        parse_specification(path) for path in sorted(directory.glob("*.md")) if path.name not in _SKIPPED_FILES
    ]
    increments.sort(key=lambda increment: tuple(int(part) for part in increment.number.split(".")))
    seen: dict[str, str] = {}
    for increment in increments:
        for rule in increment.rules:
            if rule.id in seen:
                msg = f"rule {rule.id} is defined in both {seen[rule.id]} and {increment.path}"
                raise InvalidSpecificationError(msg)
            seen[rule.id] = increment.path
    return increments
