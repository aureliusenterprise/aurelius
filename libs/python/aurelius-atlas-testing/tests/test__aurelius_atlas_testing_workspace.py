from pathlib import Path

import pytest
from aurelius_atlas_testing.workspace import (
    documents_missing_from_nav,
    files_mentioning,
    find_projects,
    load_config,
    missing_workspace_members,
    nav_documents,
)

ROOT_PYPROJECT = """
[tool.uv.workspace]
members = ["libs/python/aurelius-atlas-a", "libs/python/gone"]

[tool.aurelius-atlas.traceability]
projects = ["libs/python/aurelius-atlas-*"]
specifications = "docs/increments"
"""


def _workspace(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(ROOT_PYPROJECT)
    project = tmp_path / "libs/python/aurelius-atlas-a"
    (project / "tests").mkdir(parents=True)
    (project / "pyproject.toml").write_text('[tool.hatch.build.targets.wheel]\npackages = ["aurelius_atlas_a"]\n')
    (tmp_path / "libs/python/aurelius-atlas-npm").mkdir(parents=True)
    (tmp_path / "libs/python/aurelius-atlas-nopkg").mkdir(parents=True)
    (tmp_path / "libs/python/aurelius-atlas-nopkg/pyproject.toml").write_text("[project]\nname = 'x'\n")
    return tmp_path


@pytest.mark.covers("aurelius_atlas_testing.workspace.load_config")
@pytest.mark.covers("aurelius_atlas_testing.workspace.find_projects", rules=["TRC-04"])
def test__find_projects_keeps_python_packages(tmp_path: Path) -> None:
    """Only directories with wheel packages count; existing test directories are listed."""
    root = _workspace(tmp_path)

    projects = find_projects(root, load_config(root))

    assert [(p.path, p.packages, p.test_directories) for p in projects] == [
        ("libs/python/aurelius-atlas-a", ("aurelius_atlas_a",), ("tests",))
    ]


@pytest.mark.covers("aurelius_atlas_testing.workspace.missing_workspace_members", rules=["ADO-01"])
def test__missing_workspace_members(tmp_path: Path) -> None:
    """Members without a project directory are reported."""
    assert missing_workspace_members(_workspace(tmp_path)) == ["libs/python/gone"]


@pytest.mark.covers("aurelius_atlas_testing.workspace.nav_documents", rules=["ADO-03"])
def test__nav_documents_reads_nav_only() -> None:
    """Markdown paths are read from the nav section, titled or not."""
    text = "docs_dir: docs\nextra: x.md\nnav:\n  - index.md\n  - Title: a/b.md\n  - Group:\n      - c/d-e.md\n"

    assert nav_documents(text) == {"index.md", "a/b.md", "c/d-e.md"}
    assert nav_documents("site_name: x\n") == set()


@pytest.mark.covers("aurelius_atlas_testing.workspace.documents_missing_from_nav", rules=["ADO-03"])
def test__documents_missing_from_nav(tmp_path: Path) -> None:
    """Pages in the given sections that the nav does not list are reported."""
    (tmp_path / "docs/sec").mkdir(parents=True)
    (tmp_path / "docs/sec/in.md").write_text("")
    (tmp_path / "docs/sec/out.md").write_text("")
    (tmp_path / "mkdocs.yaml").write_text("nav:\n  - In: sec/in.md\n")

    assert documents_missing_from_nav(tmp_path, ["sec"]) == ["sec/out.md"]


@pytest.mark.covers("aurelius_atlas_testing.workspace.files_mentioning", rules=["ADO-01"])
def test__files_mentioning(tmp_path: Path) -> None:
    """Each needle found in a matching file is reported once per file."""
    (tmp_path / "a.json").write_text("uses kafka and kafka")
    (tmp_path / "b.json").write_text("clean")
    (tmp_path / "dir.json").mkdir()

    assert files_mentioning(tmp_path, ["kafka", "lambda"], ["*.json"]) == ["a.json: kafka"]


REMOVED = [
    "aurelius-kafka",
    "aurelius-aws-lambda",
    "aurelius-java-producer-example",
    "aurelius-node-red-example",
    "kafka-connect-jdbc-sink",
    "aurelius-java-example",
    "@nx/gradle",
    "gradlew",
]
WIRING = [
    "pyproject.toml",
    "package.json",
    "nx.json",
    "mkdocs.yaml",
    "**/project.json",
    ".github/workflows/*.yaml",
    ".devcontainer/devcontainer.json",
]


@pytest.mark.covers("aurelius_atlas_testing.workspace.files_mentioning", rules=["ADO-01"])
@pytest.mark.covers("aurelius_atlas_testing.workspace.missing_workspace_members", rules=["ADO-01"])
def test__workspace_has_no_references_to_removed_slices(workspace_root: Path) -> None:
    """No wiring file of this repository refers to a slice removed in increment 0.1."""
    wiring = [pattern for pattern in WIRING if "node_modules" not in pattern]
    hits = [hit for hit in files_mentioning(workspace_root, REMOVED, wiring) if "node_modules" not in hit]

    assert hits == []
    assert missing_workspace_members(workspace_root) == []


@pytest.mark.covers("aurelius_atlas_testing.workspace.documents_missing_from_nav", rules=["ADO-03"])
def test__every_decision_record_is_in_the_docs_nav(workspace_root: Path) -> None:
    """Every ADR and every conversion ledger page is reachable from the documentation."""
    assert documents_missing_from_nav(workspace_root, ["architecture/adr", "architecture/conversion"]) == []
