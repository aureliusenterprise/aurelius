"""Quality rule expressions without ``eval`` (replaces m4i-data-management ``run_quality_rule_expression``).

Aurelius rules are expressions such as ``completeness('name') | length('dataEntity', 1)``.  m4i-data-management
ran them with ``eval``; its guard only checked the outermost names, so a rule could run arbitrary Python (see
docs/migration).  Here an expression is parsed into a syntax tree and only this grammar is accepted:

    expression := call ( ('|' | '&') call )*
    call       := QUALITY_FUNCTION '(' [argument (',' argument)*] ')'
    argument   := string | number | True | False | None | '-' number | '[' [argument (',' argument)*] ']'
                | '{' [argument ':' argument (',' argument ':' argument)*] '}'

The quality functions work on a table (a list of rows; a row is a dict of column -> value) and return a score
(1 or 0) per row, with the semantics of the m4i-data-management functions of the same name: a missing column
scores 0 for every row, "empty" means ``None`` or NaN, the ``conditional_*`` functions only score the rows that
match their condition.  One deliberate difference: for ``completeness`` (and ``conditional_completeness``) an empty or
blank text and an empty list are missing as well (m4i-data-management, i.e. pandas ``notnull``, counted them as
present, so a definition cleared in the editor - saved as ``""`` - still "had a definition").  ``a | b`` scores 1 where any operand scores 1 (only operands that scored the row count),
``a & b`` where all do.  Governance quality evaluates one entity at a time: a one-row table of its attributes or
relationship attributes.
"""
from __future__ import annotations

import ast
import builtins
import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple

QUALITY_FUNCTIONS = frozenset({
    "bijacency", "compare_first_characters", "compare_first_characters_starting_without", "completeness",
    "conditional_completeness", "conditional_unallowed_text", "conditional_value", "contains_character",
    "formatting", "invalidity", "length", "new_operating_model_validity", "range", "starts_with",
    "unallowed_text", "uniqueness", "validity"})
MAX_EXPRESSION = 2000
BASKETS = ("Project", "BU direct", "Generic", "Fleet", "Yard")


class RuleSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class Call:
    function: str
    args: Tuple


@dataclass(frozen=True)
class Combined:
    op: str                 # "|" or "&"
    left: object
    right: object


def parse(expression: str):
    """Parses a rule expression into :class:`Call` / :class:`Combined` or raises :class:`RuleSyntaxError`."""
    if not isinstance(expression, str) or not expression.strip():
        raise RuleSyntaxError("empty expression")
    if len(expression) > MAX_EXPRESSION:
        raise RuleSyntaxError(f"expression longer than {MAX_EXPRESSION} characters")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as e:
        raise RuleSyntaxError(f"not valid syntax: {e.msg}") from None
    return _node(tree.body)


def _node(n):
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.BitOr, ast.BitAnd)):
        return Combined("|" if isinstance(n.op, ast.BitOr) else "&", _node(n.left), _node(n.right))
    if isinstance(n, ast.Call):
        if not isinstance(n.func, ast.Name):
            raise RuleSyntaxError("only quality functions can be called")
        if n.func.id not in QUALITY_FUNCTIONS:
            raise RuleSyntaxError(f"{n.func.id} is not a quality function")
        if n.keywords:
            raise RuleSyntaxError("keyword arguments are not supported")
        return Call(n.func.id, tuple(_arg(a) for a in n.args))
    raise RuleSyntaxError(f"unexpected {type(n).__name__}: an expression is quality function calls joined by | or &")


def _arg(n):
    if isinstance(n, ast.Constant) and (n.value is None or isinstance(n.value, (str, int, float, bool))):
        return n.value
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub) and isinstance(n.operand, ast.Constant) \
            and isinstance(n.operand.value, (int, float)) and not isinstance(n.operand.value, bool):
        return -n.operand.value
    if isinstance(n, (ast.List, ast.Tuple)):
        return [_arg(x) for x in n.elts]
    if isinstance(n, ast.Dict) and all(k is not None for k in n.keys):
        return {_hashable(_arg(k)): _arg(v) for k, v in zip(n.keys, n.values)}
    raise RuleSyntaxError(f"unsupported argument {ast.dump(n)[:80]}: only literals are allowed")


def _hashable(v):
    if isinstance(v, list):
        raise RuleSyntaxError("a list cannot be a dictionary key")
    return v


def calls(tree) -> List[Call]:
    if isinstance(tree, Call):
        return [tree]
    return calls(tree.left) + calls(tree.right)


def used_attributes(expression: str) -> List[str]:
    """The columns an expression reads (string arguments naming columns, in order, without duplicates)."""
    out: List[str] = []
    for c in calls(parse(expression)):
        for a in c.args[:_COLUMN_ARGS.get(c.function, 1)]:
            if isinstance(a, str) and a not in out:
                out.append(a)
    return out


# ---------------------------------------------------------------------------------------------- tables
class Table:
    """Rows with an index; ``columns`` = every key of any row (like a pandas DataFrame from records)."""

    def __init__(self, rows: Sequence[Mapping[str, Any]], index: Optional[Sequence[Hashable]] = None):
        self.rows = [dict(r or {}) for r in rows]
        self.index = list(index) if index is not None else list(builtins.range(len(self.rows)))
        cols = set()
        for r in self.rows:
            cols.update(r)
        self.columns = cols

    def items(self) -> Iterable[Tuple[Hashable, dict]]:
        return zip(self.index, self.rows)

    def column(self, name: str) -> List[Tuple[Hashable, Any]]:
        return [(i, r.get(name)) for i, r in self.items()]


Scores = Dict[Hashable, int]


def isna(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v))


def _zeros(t: Table) -> Scores:
    return {i: 0 for i in t.index}


def _per_value(t: Table, col: str, check: Callable[[Any], int]) -> Scores:
    if col not in t.columns:
        return _zeros(t)
    return {i: _safe(check, v) for i, v in t.column(col)}


def _safe(check, *values) -> int:
    try:
        return 1 if check(*values) else 0
    except (TypeError, ValueError, OverflowError, re.error):
        return 0


def is_blank(v) -> bool:
    """Missing for completeness: None/NaN, an empty or whitespace-only text, an empty list, set or dict."""
    if isna(v):
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, tuple, set, dict)):
        return len(v) == 0
    return False


def completeness(t: Table, column_name: str) -> Scores:
    return _per_value(t, column_name, lambda v: not is_blank(v))


def length(t: Table, column_name: str, required_length: int) -> Scores:
    def check(v):
        if not isinstance(v, list) and isna(v):
            return False
        return required_length <= len(v)
    return _per_value(t, column_name, check)


def validity(t: Table, column_name: str, values: Iterable[Any]) -> Scores:
    values = list(values)
    return _per_value(t, column_name, lambda v: v in values)


def invalidity(t: Table, column_name: str, values: Iterable[Any]) -> Scores:
    if column_name not in t.columns:
        return _zeros(t)
    return {i: 1 - s for i, s in validity(t, column_name, values).items()}


def formatting(t: Table, column_name: str, pattern: str) -> Scores:
    regex = re.compile(pattern)
    return _per_value(t, column_name, lambda v: not isna(v) and regex.match(str(v)) is not None)


def range(t: Table, column_name: str, lower_bound: float = 0, upper_bound: float = 1) -> Scores:  # noqa: A001
    return _per_value(t, column_name, lambda v: not isna(v) and lower_bound <= int(v) <= upper_bound)


def starts_with(t: Table, column_name: str, *prefixes: str) -> Scores:
    return _per_value(t, column_name, lambda v: isna(v) or str(v).startswith(tuple(prefixes)))


def unallowed_text(t: Table, column_name: str, text: str) -> Scores:
    return _per_value(t, column_name, lambda v: isna(v) or text not in str(v))


def contains_character(t: Table, column_name: str, substring: str, expected_count: int = 1) -> Scores:
    return _per_value(t, column_name, lambda v: isna(v) or str(v).count(substring) >= expected_count)


def uniqueness(t: Table, column_name: str) -> Scores:
    if column_name not in t.columns:
        return _zeros(t)
    seen: Dict[str, set] = {}
    for i, v in t.column(column_name):
        if not isna(v):
            seen.setdefault(str(v), set()).add(str(i))
    return {i: 1 if isna(v) or len(seen[str(v)]) == 1 else 0 for i, v in t.column(column_name)}


def bijacency(t: Table, column_a: str, column_b: str) -> Scores:
    if column_a not in t.columns or column_b not in t.columns:
        return _zeros(t)
    fwd: Dict[str, set] = {}
    inv: Dict[str, set] = {}
    pairs = [(i, str(r.get(column_a)), str(r.get(column_b))) for i, r in t.items()]
    for _, a, b in pairs:
        fwd.setdefault(a, set()).add(b)
        inv.setdefault(b, set()).add(a)
    return {i: 1 if len(fwd[a]) <= 1 and len(inv[b]) <= 1 else 0 for i, a, b in pairs}


def compare_first_characters(t: Table, first_column_name: str, second_column_name: str,
                             number_of_characters: int = 1) -> Scores:
    if first_column_name not in t.columns or second_column_name not in t.columns:
        return _zeros(t)

    def check(a, b):
        if isna(a) or isna(b):
            return False
        return str(a)[:number_of_characters] == str(b)[:number_of_characters]
    return {i: _safe(check, r.get(first_column_name), r.get(second_column_name)) for i, r in t.items()}


def compare_first_characters_starting_without(t: Table, first_column_name: str, second_column_name: str,
                                              number_of_characters: int, *prefixes: str) -> Scores:
    if first_column_name not in t.columns or second_column_name not in t.columns:
        return _zeros(t)
    same = compare_first_characters(t, first_column_name, second_column_name, number_of_characters)
    starts = starts_with(t, first_column_name, *prefixes)
    return {i: 1 if same[i] == 1 and starts[i] == 0 else 0 for i in t.index}


def _matching(t: Table, key_column: str, values: Iterable[str]) -> Table:
    values = list(values)
    keep = [(i, r) for i, r in t.items()
            if isinstance(r.get(key_column), str) and any(v in r[key_column] for v in values)]
    sub = Table([r for _, r in keep], [i for i, _ in keep])
    sub.columns = t.columns
    return sub


def conditional_completeness(t: Table, key_column: str, value_column: str, values: Iterable[str]) -> Scores:
    if key_column not in t.columns or value_column not in t.columns:
        return _zeros(t)
    return completeness(_matching(t, key_column, values), value_column)


def conditional_unallowed_text(t: Table, key_column: str, value_column: str, values: Iterable[str],
                               text: str) -> Scores:
    if key_column not in t.columns or value_column not in t.columns:
        return _zeros(t)
    return unallowed_text(_matching(t, key_column, values), value_column, text)


def conditional_value(t: Table, key_column: str, value_column: str, value_mapping: Mapping[Any, Any]) -> Scores:
    if key_column not in t.columns or value_column not in t.columns:
        return _zeros(t)
    out: Scores = {}
    for i, r in t.items():
        key = r.get(key_column)
        try:
            if key not in value_mapping:
                continue
        except TypeError:
            continue
        expected = value_mapping[key]
        v = r.get(value_column)
        out[i] = _safe(lambda: v in expected if isinstance(expected, (list, set)) else v == expected)
    return out


def new_operating_model_validity(t: Table, basket_column: str, hierarchical_org: str, functional_org: str) -> Scores:
    if any(c not in t.columns for c in (basket_column, hierarchical_org, functional_org)):
        return _zeros(t)
    return {i: 1 if r.get(basket_column) not in BASKETS or r.get(hierarchical_org) == r.get(functional_org) else 0
            for i, r in t.items()}


FUNCTIONS: Dict[str, Callable[..., Scores]] = {
    "bijacency": bijacency, "compare_first_characters": compare_first_characters,
    "compare_first_characters_starting_without": compare_first_characters_starting_without,
    "completeness": completeness, "conditional_completeness": conditional_completeness,
    "conditional_unallowed_text": conditional_unallowed_text, "conditional_value": conditional_value,
    "contains_character": contains_character, "formatting": formatting, "invalidity": invalidity,
    "length": length, "new_operating_model_validity": new_operating_model_validity, "range": range,
    "starts_with": starts_with, "unallowed_text": unallowed_text, "uniqueness": uniqueness, "validity": validity}
assert set(FUNCTIONS) == QUALITY_FUNCTIONS
# how many leading arguments name columns (used_attributes)
_COLUMN_ARGS = {"bijacency": 2, "compare_first_characters": 2, "compare_first_characters_starting_without": 2,
                "conditional_completeness": 2, "conditional_unallowed_text": 2, "conditional_value": 2,
                "new_operating_model_validity": 3}


def evaluate(tree, table: Table) -> Scores:
    if isinstance(tree, Call):
        try:
            return FUNCTIONS[tree.function](table, *tree.args)
        except TypeError as e:          # wrong number of arguments
            raise RuleSyntaxError(f"{tree.function}: {e}") from None
    left, right = evaluate(tree.left, table), evaluate(tree.right, table)
    out: Scores = {}
    for i in table.index:
        vals = [s[i] for s in (left, right) if i in s]
        if vals:
            out[i] = int(any(vals)) if tree.op == "|" else int(all(vals))
    return out


def run(expression: str, rows: Sequence[Mapping[str, Any]], index: Optional[Sequence[Hashable]] = None) -> Scores:
    """Scores of ``expression`` for each row (rows the expression does not apply to are left out)."""
    return evaluate(parse(expression), Table(rows, index))


def run_one(expression: str, row: Mapping[str, Any]) -> Optional[int]:
    """Score of ``expression`` for a single row (governance quality): 1, 0, or None if it does not apply."""
    return run(expression, [row]).get(0)
