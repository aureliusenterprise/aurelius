"""Which projects and specifications the traceability check covers.

Configured in the root ``pyproject.toml``::

    [tool.aurelius-atlas.traceability]
    projects = ["libs/python/aurelius-atlas-*", "apps/aurelius-atlas-*"]
    specifications = "docs/architecture/conversion/increments"
"""

import re
import tomllib
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict

TEST_DIRECTORIES = ("tests", "e2e")


class TraceabilityConfig(BaseModel):
    """The ``[tool.aurelius-atlas.traceability]`` table.

    Attributes:
        projects: Glob patterns of project directories, relative to the workspace root.
        specifications: Directory of increment specifications.
    """

    model_config = ConfigDict(frozen=True)

    projects: tuple[str, ...]
    specifications: str


class Project(BaseModel):
    """A Python project whose public API must be traceable.

    Attributes:
        path: The project directory, relative to the workspace root.
        packages: Its importable package directories, relative to the project.
        test_directories: Its test directories that exist, relative to the project.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    packages: tuple[str, ...]
    test_directories: tuple[str, ...]


def load_config(root: Path) -> TraceabilityConfig:
    """Read the traceability configuration from the workspace's ``pyproject.toml``.

    Args:
        root: The workspace root.

    Returns:
        The configuration.

    Raises:
        KeyError: If the table is missing.
    """
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return TraceabilityConfig.model_validate(data["tool"]["aurelius-atlas"]["traceability"])


def find_projects(root: Path, config: TraceabilityConfig) -> list[Project]:
    """List the Python projects matched by the configured patterns.

    A directory counts when it has a ``pyproject.toml`` declaring wheel packages.

    Args:
        root: The workspace root.
        config: The traceability configuration.

    Returns:
        The projects, sorted by path.
    """
    projects: dict[str, Project] = {}
    for pattern in config.projects:
        for directory in root.glob(pattern):
            manifest = directory / "pyproject.toml"
            if not manifest.is_file():
                continue
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
            packages = data.get("tool", {}).get("hatch", {}).get("build", {}).get("targets", {}).get("wheel", {})
            names = tuple(packages.get("packages", ()))
            if not names:
                continue
            path = directory.relative_to(root).as_posix()
            tests = tuple(name for name in TEST_DIRECTORIES if (directory / name).is_dir())
            projects[path] = Project(path=path, packages=names, test_directories=tests)
    return [projects[path] for path in sorted(projects)]


_NAV_START = re.compile(r"^nav:", re.MULTILINE)
_NAV_DOCUMENT = re.compile(r"(?:^|:\s|-\s)([\w./-]+\.md)\s*$", re.MULTILINE)


def nav_documents(mkdocs_text: str) -> set[str]:
    """Return every Markdown path the ``nav`` section of ``mkdocs.yaml`` lists.

    Args:
        mkdocs_text: The content of ``mkdocs.yaml``.

    Returns:
        Paths relative to the docs directory.
    """
    start = _NAV_START.search(mkdocs_text)
    if start is None:
        return set()
    return set(_NAV_DOCUMENT.findall(mkdocs_text[start.start() :]))


def documents_missing_from_nav(root: Path, sections: Sequence[str]) -> list[str]:
    """List documents in the given docs sections that the navigation does not reach.

    Args:
        root: The workspace root (with ``mkdocs.yaml`` and ``docs/``).
        sections: Directories under ``docs/`` whose every page must be in the nav.

    Returns:
        Unreachable documents, relative to ``docs/``, sorted.
    """
    listed = nav_documents((root / "mkdocs.yaml").read_text(encoding="utf-8"))
    docs = root / "docs"
    present = {path.relative_to(docs).as_posix() for section in sections for path in (docs / section).rglob("*.md")}
    return sorted(present - listed)


def missing_workspace_members(root: Path) -> list[str]:
    """List uv workspace members in the root ``pyproject.toml`` whose directory is gone.

    Args:
        root: The workspace root.

    Returns:
        The missing member paths, sorted.
    """
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    members = data.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    return sorted(member for member in members if not (root / member / "pyproject.toml").is_file())


def files_mentioning(root: Path, needles: Sequence[str], files: Sequence[str]) -> list[str]:
    """List ``file: needle`` for every needle found in the given workspace files.

    Args:
        root: The workspace root.
        needles: Strings that must not appear (for example names of removed projects).
        files: Glob patterns of files to search, relative to the root.

    Returns:
        One ``path: needle`` entry per hit, sorted.
    """
    hits = set()
    for pattern in files:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            hits.update(f"{path.relative_to(root).as_posix()}: {needle}" for needle in needles if needle in text)
    return sorted(hits)
