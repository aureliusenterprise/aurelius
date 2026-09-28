"""Structural JSON comparison with an allow-list.

``diff(left, right, rules)`` returns a list of :class:`Difference` (``path``, ``left``, ``right``).  Paths are
tuples of keys / list indexes; printed as ``a.b[3].c``.  Rules (an allow-list, usually loaded from a JSON file)
say which differences are accepted:

``ignore``
    glob patterns of paths that are not compared at all, e.g. ``"*.updateTime"``, ``"entity.version"``,
    ``"**.guid"`` (``*`` matches one path element, ``**`` any number).
``unordered``
    glob patterns of lists compared as multisets (order is not significant), e.g. ``"classifications"``.
``empty_equals_missing``
    when true (default), ``None``, ``[]``, ``{}``, ``""`` and a missing key are treated as the same value.
``float_tolerance``
    absolute tolerance for numbers (default 1e-9), e.g. for rounded quality scores.
"""
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple, Union

MISSING = object()
_EMPTY = (None, [], {}, "")

Path_ = Tuple[Union[str, int], ...]


@dataclass
class Rules:
    ignore: List[str] = field(default_factory=list)
    unordered: List[str] = field(default_factory=list)
    empty_equals_missing: bool = True
    float_tolerance: float = 1e-9

    @classmethod
    def load(cls, path: Optional[Union[str, Path]]) -> "Rules":
        if not path:
            return cls()
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def merged(self, other: "Rules") -> "Rules":
        return Rules(self.ignore + other.ignore, self.unordered + other.unordered,
                     self.empty_equals_missing and other.empty_equals_missing,
                     max(self.float_tolerance, other.float_tolerance))


@dataclass
class Difference:
    path: Path_
    left: Any
    right: Any

    @property
    def where(self) -> str:
        return format_path(self.path)

    def as_dict(self) -> dict:
        return {"path": self.where, "left": _show(self.left), "right": _show(self.right)}


def _show(v):
    return "<missing>" if v is MISSING else v


def format_path(path: Sequence[Union[str, int]]) -> str:
    out = ""
    for p in path:
        out += f"[{p}]" if isinstance(p, int) else (f".{p}" if out else str(p))
    return out or "<root>"


def _match(path: Path_, patterns: Iterable[str]) -> bool:
    names = [str(p) if not isinstance(p, int) else "[]" for p in path]
    for pat in patterns:
        if _glob(names, pat.split(".")):
            return True
    return False


def _glob(names: List[str], parts: List[str]) -> bool:
    if not parts:
        return not names
    head, rest = parts[0], parts[1:]
    if head == "**":
        return any(_glob(names[i:], rest) for i in range(len(names) + 1))
    if not names:
        return False
    if names[0] == "[]":                   # list indexes are transparent to patterns
        return _glob(names[1:], parts)
    return fnmatch.fnmatchcase(names[0], head) and _glob(names[1:], rest)


def _is_empty(v) -> bool:
    return v is MISSING or any(v is e or (type(v) is type(e) and v == e) for e in _EMPTY)


def _canon(v) -> str:
    return json.dumps(v, sort_keys=True, default=str)


def diff(left: Any, right: Any, rules: Optional[Rules] = None, path: Path_ = ()) -> List[Difference]:
    rules = rules or Rules()
    out: List[Difference] = []
    _diff(left, right, rules, tuple(path), out)
    return out


def _diff(a, b, rules: Rules, path: Path_, out: List[Difference]) -> None:
    if path and _match(path, rules.ignore):
        return
    if rules.empty_equals_missing and _is_empty(a) and _is_empty(b):
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            _diff(a.get(k, MISSING), b.get(k, MISSING), rules, path + (k,), out)
        return
    if isinstance(a, list) and isinstance(b, list):
        if _match(path, rules.unordered):
            _diff_unordered(a, b, rules, path, out)
            return
        for i in range(max(len(a), len(b))):
            _diff(a[i] if i < len(a) else MISSING, b[i] if i < len(b) else MISSING, rules, path + (i,), out)
        return
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) \
            and not isinstance(b, bool):
        if abs(a - b) > rules.float_tolerance:
            out.append(Difference(path, a, b))
        return
    if a != b:
        out.append(Difference(path, a, b))


def _diff_unordered(a: list, b: list, rules: Rules, path: Path_, out: List[Difference]) -> None:
    # pair equal elements first (compared with the ignore rules applied), report the rest
    rest_b = list(b)
    unmatched_a = []
    for x in a:
        for i, y in enumerate(rest_b):
            if not diff(x, y, rules, path + (0,)):
                del rest_b[i]
                break
        else:
            unmatched_a.append(x)
    for x, y in zip(sorted(unmatched_a, key=_canon), sorted(rest_b, key=_canon)):
        out.append(Difference(path + ("*",), x, y))
    extra = len(unmatched_a) - len(rest_b)
    for x in (sorted(unmatched_a, key=_canon)[len(rest_b):] if extra > 0 else []):
        out.append(Difference(path + ("*",), x, MISSING))
    for y in (sorted(rest_b, key=_canon)[len(unmatched_a):] if extra < 0 else []):
        out.append(Difference(path + ("*",), MISSING, y))
