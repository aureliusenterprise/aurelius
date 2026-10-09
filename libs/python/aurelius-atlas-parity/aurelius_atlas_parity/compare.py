"""Comparing a candidate answer with the recorded reference answer."""

import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from aurelius_atlas_parity.results import ParityResult
from aurelius_atlas_parity.scenario import Allowance, Step


class Difference(BaseModel):
    """One place where two documents differ.

    Attributes:
        path: Where, as a concrete path such as ``$.entities[2].guid``.
        expected: The reference value (``None`` if missing there).
        actual: The candidate value (``None`` if missing there).
    """

    model_config = ConfigDict(frozen=True)

    path: str
    expected: Any = None
    actual: Any = None

    def describe(self) -> str:
        """Return a one-line description for reports.

        Returns:
            For example ``"$.name: expected 'a', got 'b'"``.
        """
        return f"{self.path}: expected {self.expected!r}, got {self.actual!r}"[:300]


_MISSING = object()


def differences(expected: Any, actual: Any, path: str = "$") -> list[Difference]:  # noqa: ANN401
    """List every difference between two JSON documents.

    Args:
        expected: The reference document.
        actual: The candidate document.
        path: The path of these documents within their parents.

    Returns:
        Differences in document order; an empty list when equal.
    """
    if isinstance(expected, dict) and isinstance(actual, dict):
        found: list[Difference] = []
        for key in sorted(set(expected) | set(actual)):
            child = f"{path}.{key}" if re.fullmatch(r"[A-Za-z_][\w-]*", key) else f"{path}[{key!r}]"
            left, right = expected.get(key, _MISSING), actual.get(key, _MISSING)
            if left is _MISSING or right is _MISSING:
                found.append(
                    Difference(
                        path=child,
                        expected=None if left is _MISSING else left,
                        actual=None if right is _MISSING else right,
                    )
                )
            else:
                found += differences(left, right, child)
        return found
    if isinstance(expected, list) and isinstance(actual, list):
        found = []
        for index in range(max(len(expected), len(actual))):
            child = f"{path}[{index}]"
            if index >= len(expected) or index >= len(actual):
                found.append(
                    Difference(
                        path=child,
                        expected=expected[index] if index < len(expected) else None,
                        actual=actual[index] if index < len(actual) else None,
                    )
                )
            else:
                found += differences(expected[index], actual[index], child)
        return found
    if type(expected) is not type(actual) or expected != actual:
        return [Difference(path=path, expected=expected, actual=actual)]
    return []


def pattern_of(path: str) -> re.Pattern[str]:
    """Return a regex matching concrete paths at or below an allowance path.

    ``[*]`` matches any index and ``..key`` matches ``key`` at any depth.

    Args:
        path: An allowance path such as ``$.entities[*].attributes``.

    Returns:
        The compiled pattern.
    """
    regex = re.escape(path).replace(r"\[\*\]", r"\[\d+\]")
    regex = re.sub(r"\\\.\\\.", r"(?:\\..*)?\\.", regex)
    return re.compile(f"^{regex}(?:$|[.\\[])")


def allowance_for(difference: Difference, allowances: tuple[Allowance, ...]) -> Allowance | None:
    """Return the first allowance covering a difference's path, if any.

    Args:
        difference: A difference.
        allowances: The step's allowances.

    Returns:
        The allowance, or ``None``.
    """
    return next((allowance for allowance in allowances if pattern_of(allowance.path).match(difference.path)), None)


def judge(
    scenario: str,
    step: Step,
    endpoint: str,
    expected: tuple[int, Any],
    actual: tuple[int, Any],
) -> ParityResult:
    """Compare one step's normalised answers and decide its status.

    Args:
        scenario: The scenario name.
        step: The step.
        endpoint: The step's endpoint description.
        expected: ``(status code, body)`` recorded from the reference.
        actual: ``(status code, body)`` of the candidate.

    Returns:
        ``match`` when equal; ``deviation`` when every difference is allowed; else ``mismatch``.
    """
    found = differences(expected[1], actual[1])
    if expected[0] != actual[0]:
        found.insert(0, Difference(path="HTTP status", expected=expected[0], actual=actual[0]))
    if not found:
        return ParityResult(scenario=scenario, step=step.name, endpoint=endpoint, status="match")
    allowed = [allowance_for(difference, step.deviations) for difference in found]
    if all(allowed):
        ids = ", ".join(sorted({allowance.id for allowance in allowed if allowance}))
        return ParityResult(scenario=scenario, step=step.name, endpoint=endpoint, status="deviation", deviation=ids)
    unexplained = [difference for difference, allowance in zip(found, allowed, strict=True) if allowance is None]
    detail = "; ".join(difference.describe() for difference in unexplained[:3])
    if len(unexplained) > 3:  # noqa: PLR2004
        detail += f"; and {len(unexplained) - 3} more"
    return ParityResult(scenario=scenario, step=step.name, endpoint=endpoint, status="mismatch", detail=detail)
