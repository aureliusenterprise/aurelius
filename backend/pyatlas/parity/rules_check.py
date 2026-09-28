"""Phase 0 inventory: can every existing quality rule expression be run without ``eval``?

Aurelius evaluates rule expressions such as ``completeness('name') | length('dataEntity', 1)`` with ``eval``
(m4i-data-management ``run_quality_rule_expression``).  Its guard, ``validate_function_string``, only checks
the names of the outermost code object, so names inside a nested ``lambda`` or comprehension are not checked
and an expression can reach arbitrary Python objects.  pyatlas will parse expressions into a syntax tree and
accept only this grammar (see :func:`parse`):

    expression := call ( ('|' | '&') call )*
    call       := QUALITY_FUNCTION '(' [argument (',' argument)*] ')'
    argument   := string | number | True | False | None | '-' number | '[' [argument (',' argument)*] ']'
                | '{' [argument ':' argument (',' argument ':' argument)*] '}'

This check parses every expression found in the given sources and lists the ones that fall outside it.
"""
from __future__ import annotations

import ast
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple

from .report import Report

# the quality functions of m4i-data-management (core/quality/rules), which are the only callable names
QUALITY_FUNCTIONS = frozenset({
    "bijacency", "compare_first_characters", "compare_first_characters_starting_without", "completeness",
    "conditional_completeness", "conditional_unallowed_text", "conditional_value", "contains_character",
    "formatting", "invalidity", "length", "new_operating_model_validity", "range", "starts_with",
    "unallowed_text", "uniqueness", "validity"})
QUALITY_TYPES = ("m4i_data_quality", "m4i_gov_data_quality")


class RuleSyntaxError(ValueError):
    pass


@dataclass
class Call:
    function: str
    args: Tuple


@dataclass
class Combined:
    op: str                 # "|" or "&"
    left: object
    right: object


def parse(expression: str):
    """Parses a rule expression into :class:`Call` / :class:`Combined` or raises :class:`RuleSyntaxError`."""
    if not isinstance(expression, str) or not expression.strip():
        raise RuleSyntaxError("empty expression")
    if len(expression) > 2000:
        raise RuleSyntaxError("expression longer than 2000 characters")
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
        return {_arg(k): _arg(v) for k, v in zip(n.keys, n.values)}
    raise RuleSyntaxError(f"unsupported argument {ast.dump(n)[:80]}: only literals are allowed")


# ---------------------------------------------------------------------------------------------- sources
def rules_from_definitions(folder: Path) -> Iterator[Tuple[str, str]]:
    for f in sorted(Path(folder).glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            yield f"{f.name}#{r.get('id')} {r.get('qualifiedName')}", r.get("expression")


def rules_from_documents(path: Path) -> Iterator[Tuple[str, str]]:
    for d in json.loads(Path(path).read_text(encoding="utf-8")):
        if d.get("expression") is not None:
            yield f"{Path(path).name} {d.get('id')}", d["expression"]


def rules_from_export(path: Path) -> Iterator[Tuple[str, str]]:
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        if n.startswith("atlas-") or not n.endswith(".json"):
            continue
        e = json.loads(z.read(n)).get("entity") or {}
        if e.get("typeName") in QUALITY_TYPES:
            a = e.get("attributes") or {}
            yield f"{Path(path).name} {e.get('typeName')} {a.get('qualifiedName')}", a.get("expression")


def rules_from_server(client) -> Iterator[Tuple[str, str]]:
    from .store import LiveSource
    for e in LiveSource(client, QUALITY_TYPES).entities():
        a = e.get("attributes") or {}
        yield f"{client.name} {e.get('typeName')} {a.get('qualifiedName')}", a.get("expression")


def check(rules: Iterable[Tuple[str, Optional[str]]], report: Optional[Report] = None) -> Report:
    report = report or Report("quality-rules", "rule expressions", "safe grammar")
    seen = set()
    functions = {}
    for item, expr in rules:
        try:
            tree = parse(expr)
        except RuleSyntaxError as e:
            today = " (rejected by today's validate_function_string as well)" \
                if "is not a quality function" in str(e) else ""
            report.error(item, f"{e}{today} -- expression: {expr!r}")
            continue
        report.ok()
        seen.add(expr)
        for c in _calls(tree):
            functions[c.function] = functions.get(c.function, 0) + 1
    report.stats["distinct valid expressions"] = len(seen)
    report.stats.update({f"uses {k}": v for k, v in sorted(functions.items())})
    return report


def _calls(t) -> List[Call]:
    if isinstance(t, Call):
        return [t]
    return _calls(t.left) + _calls(t.right)
