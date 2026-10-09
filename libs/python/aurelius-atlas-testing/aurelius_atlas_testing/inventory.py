"""The public API of a package: every function that needs a test (ADR 049).

The inventory is read from source with :mod:`ast`, so nothing is imported or executed.
Public means: not starting with an underscore, at module level or as a member of a
public module-level class (DD-006). Private modules (``_name.py``) and ``__main__`` are skipped.
"""

import ast
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

Kind = Literal["function", "method", "property", "class"]


class ApiItem(BaseModel):
    """One public, testable element of a package.

    Attributes:
        target: Dotted path, as a ``covers`` marker names it.
        kind: Function, method, property or class.
        path: Source file, relative to the inventoried package's parent directory.
        line: Line of the definition.
    """

    model_config = ConfigDict(frozen=True)

    target: str
    kind: Kind
    path: str
    line: int


def is_public(name: str) -> bool:
    """Return whether a name is public (does not start with an underscore).

    Args:
        name: A module, class, function or attribute name.

    Returns:
        ``True`` for public names.
    """
    return not name.startswith("_")


def module_name(package_dir: Path, source: Path) -> str:
    """Return the dotted module name of a source file inside a package.

    Args:
        package_dir: The package directory (its name is the top-level package).
        source: A ``.py`` file inside it.

    Returns:
        The dotted name; ``__init__.py`` maps to its package.
    """
    relative = source.relative_to(package_dir.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _is_property(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a method is decorated as a property."""
    return any(
        (isinstance(decorator, ast.Name) and decorator.id in {"property", "cached_property"})
        or (isinstance(decorator, ast.Attribute) and decorator.attr in {"setter", "cached_property"})
        for decorator in node.decorator_list
    )


def items_in_module(tree: ast.Module, module: str, path: str) -> list[ApiItem]:
    """List the public functions, classes and members defined in one parsed module.

    Args:
        tree: The parsed module.
        module: Its dotted name.
        path: Its path for reporting.

    Returns:
        The public items, in source order. A class is listed itself only when it has
        behaviour (methods) but no public ones, for example a model whose logic lives in
        private validators; pure data classes and plain exceptions are not listed (DD-006).
    """
    items: list[ApiItem] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(node.name):
            items.append(ApiItem(target=f"{module}.{node.name}", kind="function", path=path, line=node.lineno))
        elif isinstance(node, ast.ClassDef) and is_public(node.name):
            members = [
                ApiItem(
                    target=f"{module}.{node.name}.{member.name}",
                    kind="property" if _is_property(member) else "method",
                    path=path,
                    line=member.lineno,
                )
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(member.name)
            ]
            has_behaviour = any(isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) for member in node.body)
            if members:
                items.extend(members)
            elif has_behaviour:
                items.append(ApiItem(target=f"{module}.{node.name}", kind="class", path=path, line=node.lineno))
    return items


def inventory(package_dir: Path) -> list[ApiItem]:
    """List the public API of a package directory.

    Args:
        package_dir: The importable package (the directory containing ``__init__.py``).

    Returns:
        All public items, sorted by target.
    """
    items: list[ApiItem] = []
    for source in sorted(package_dir.rglob("*.py")):
        relative = source.relative_to(package_dir)
        if any(not is_public(part) for part in relative.with_suffix("").parts if part != "__init__"):
            continue
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        path = str(source.relative_to(package_dir.parent))
        items.extend(items_in_module(tree, module_name(package_dir, source), path))
    return sorted(items, key=lambda item: item.target)
