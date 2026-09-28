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

import json
import zipfile
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple

from .report import Report

from pyatlas.aurelius.quality_rules import (  # noqa: F401 - the grammar lives in pyatlas (phase 3)
    QUALITY_FUNCTIONS, Call, Combined, RuleSyntaxError, parse)
from pyatlas.aurelius.quality_rules import calls as _calls

QUALITY_TYPES = ("m4i_data_quality", "m4i_gov_data_quality")


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

