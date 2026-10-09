"""A small JSON path language for scenarios and normalisation rules.

Supported forms, enough for Atlas responses:

- ``$`` — the whole document
- ``$.a.b`` — object members
- ``$.a[*].b`` — every element of a list
- ``$.a[0]`` — one element of a list
- ``$..key`` — the member ``key`` at any depth
"""

import re
from collections.abc import Callable, Iterator
from typing import Any

type Json = Any
_TOKEN = re.compile(r"\.\.([A-Za-z_][\w-]*)|\.([A-Za-z_][\w-]*)|\[(\*|\d+)\]")


class InvalidPathError(ValueError):
    """A path does not follow the supported syntax."""


def parse_path(path: str) -> list[tuple[str, str]]:
    """Split a path into ``(kind, value)`` steps.

    Args:
        path: A path such as ``$.entities[*].guid``.

    Returns:
        Steps of kind ``member``, ``deep``, ``all`` or ``index``.

    Raises:
        InvalidPathError: If the path is malformed.
    """
    if not path.startswith("$"):
        msg = f"path {path!r} must start with '$'"
        raise InvalidPathError(msg)
    steps: list[tuple[str, str]] = []
    position = 1
    while position < len(path):
        match = _TOKEN.match(path, position)
        if match is None:
            msg = f"path {path!r} is malformed at position {position}"
            raise InvalidPathError(msg)
        deep, member, index = match.groups()
        if deep is not None:
            steps.append(("deep", deep))
        elif member is not None:
            steps.append(("member", member))
        else:
            steps.append(("all", "*") if index == "*" else ("index", index))
        position = match.end()
    return steps


def _walk_deep(document: Json, key: str) -> Iterator[tuple[Json, str]]:
    """Yield every ``(container, key)`` where ``key`` occurs, at any depth."""
    if isinstance(document, dict):
        for name, value in document.items():
            if name == key:
                yield document, name
            yield from _walk_deep(value, key)
    elif isinstance(document, list):
        for value in document:
            yield from _walk_deep(value, key)


def locate(document: Json, path: str) -> list[tuple[Json, str | int]]:
    """Return every ``(container, key)`` pair the path points at.

    Args:
        document: A parsed JSON document.
        path: A path; ``$`` alone is not locatable (it has no container).

    Returns:
        The locations that exist in the document; missing members are skipped.
    """
    steps = parse_path(path)
    if not steps:
        return []
    current: list[tuple[Json, str | int | None]] = [(None, None)]
    values: list[Json] = [document]
    for number, (kind, value) in enumerate(steps):
        last = number == len(steps) - 1
        next_locations: list[tuple[Json, str | int | None]] = []
        next_values: list[Json] = []
        for item in values:
            pairs: list[tuple[Json, str | int]] = []
            if kind == "member" and isinstance(item, dict) and value in item:
                pairs = [(item, value)]
            elif kind == "deep":
                pairs = list(_walk_deep(item, value))
            elif kind == "all" and isinstance(item, list):
                pairs = [(item, position) for position in range(len(item))]
            elif kind == "index" and isinstance(item, list) and int(value) < len(item):
                pairs = [(item, int(value))]
            for container, key in pairs:
                next_locations.append((container, key))
                next_values.append(container[key])
        current, values = next_locations, next_values
        if last:
            break
    return [(container, key) for container, key in current if key is not None]


def select(document: Json, path: str) -> list[Json]:
    """Return the values the path points at.

    Args:
        document: A parsed JSON document.
        path: A path; ``$`` returns the whole document.

    Returns:
        The values, in document order.
    """
    if path == "$":
        return [document]
    return [container[key] for container, key in locate(document, path)]


def transform(document: Json, path: str, function: Callable[[Json], Json]) -> None:
    """Replace, in place, every value the path points at by ``function(value)``.

    Args:
        document: A parsed JSON document, changed in place.
        path: Where to apply the function.
        function: The replacement function.
    """
    for container, key in locate(document, path):
        container[key] = function(container[key])
