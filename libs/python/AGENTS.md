# Python Libraries (libs/python)

This directory holds Python workspace libraries consumed by the apps.
This file is the recipe for adding or modifying a library here.

## Adding a New Library

1. **Scaffold** `libs/python/<name>/`:
    - `<package_name>/` — the importable package (snake_case)
    - `README.md` — what the library does and when to use it. This is the
      canonical description: each library documents itself here, so no central
      list of libraries is maintained anywhere.
    - `tests/test__*.py` — pytest tests, `conftest.py` for fixtures
    - `pyproject.toml` — hatchling build backend,
      `[tool.hatch.build.targets.wheel] packages = ["<package_name>"]`,
      `requires-python = ">=3.14"`, pytest asyncio `auto` mode config
    - `project.json` — `projectType: "library"`, `sourceRoot` pointing at the package
    - `sonar-project.properties` — copy from a sibling lib
2. **Register in root `pyproject.toml`** (all three, or `uv sync` won't resolve it):
    - `[tool.uv.workspace]` members
    - `[dependency-groups] dev`
    - `[tool.uv.sources.<name>] workspace = true`
3. **Consume from an app**: add the dep to the app's `pyproject.toml`
   `[project.dependencies]` plus its own `[tool.uv.sources.<name>] workspace = true`.
4. **Docs**: add an mkdocstrings page under `docs/api-reference/libs/python/`
   and register it in `mkdocs.yaml` nav.
5. **Run** `uv sync`, then `uv run pytest libs/python/<name>` and
   `uv run pyright libs/python/<name>`.

## Conventions

- Dependencies are declared per-package; the root venv at `.venv/` resolves the
  whole workspace. Never add a path dependency — use `workspace = true` sources.
- Type hints everywhere; pyright `standard` mode must pass. Ruff `select = ["ALL"]`
  with the root ignores — do not add per-file ignores without a comment why.
- Google-style docstrings (mkdocstrings renders them into the API reference).
- Tests are `test__*.py` under `tests/` (not co-located, unlike TypeScript).
- Libraries must not read env vars directly; accept settings objects or explicit
  parameters so apps own configuration via pydantic-settings.
- Keep libraries import-light: heavy/optional integrations go behind pip extras.

## Removal

Removing a library means: delete the directory, remove it from root `pyproject.toml`
(members, dev group, uv.sources), remove it from every consuming app's
`pyproject.toml`, delete its `mkdocs.yaml` nav entry and API reference page, and
check `implicitDependencies` in consuming apps' `project.json` files.
