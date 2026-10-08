# Workspace Context

This is the **Aurelius Project Template** — a polyglot monorepo for bootstrapping enterprise microservice projects.

This file covers **workspace-wide** rules only. Every project has its own
colocated `AGENTS.md` (wiring, conventions, removal) and `README.md` (what it
is). Before editing a project, read its `AGENTS.md` and `README.md` first —
there is no central index.

## Quick Start

1. **Install dependencies**: `npm ci` (root) + `uv sync` + `./gradlew dependencies` (Java)
2. **Run an app**: `npx nx serve <project>` — required dev infrastructure (Keycloak, Postgres,
   Kafka, observability) starts automatically via target `dependsOn`; there is no root compose file.
3. **Run pre-commit**: `pre-commit run --all-files` (fix any issues)
4. **Verify**: `nx run-many --target=test -c ci` (or target a specific project)

> [!WARNING]
> Fresh clones fail tests until a SOPS age key exists (`secrets/keys.txt`, generated on first
> devcontainer start) AND the key is registered in `.sops.yaml`. Nearly every `test`/`serve`/`e2e`
> target `dependsOn` `decrypt`, which fails with a SOPS/age error otherwise — that is a setup gap,
> not a code bug.
>
> [!NOTE]
> This is a **template** — apps/libs are starting points, not production-ready as-is.
> Modules are designed to be removable; see the [Module Map](#module-map).

## Target Discovery

Most Nx targets are **inferred** by the custom plugins in `tools/plugins/*.ts` from file globs
(`pyproject.toml`, `Dockerfile`, `.env`, `.env.enc`, `mkdocs.yaml`, …). A `project.json` usually
declares only one or two targets; `build`, `test`, `lint`, `typecheck`, `e2e`, `docker-*`,
`decrypt`/`encrypt`/`keygen`/`update-keys`, `sonar`, and `docs` are mostly invisible in it.

**Never infer the runnable target set from `project.json` alone.** Query the graph:

```bash
npx nx show project <project-name> --json
```

## Verification Tiers

Pick the cheapest tier that covers your change; state which you ran.

| Tier | Requirement                 | Commands                                                                                  |
| ---- | --------------------------- | ----------------------------------------------------------------------------------------- |
| 0    | Offline (no key, no Docker) | `nx lint <project>`, `nx typecheck <project>` (Python), `uv run pytest <app>/tests`       |
| 1    | SOPS key registered         | `nx test <project> -c ci` (unit tests; `dependsOn` decrypt)                               |
| 2    | Docker runtime              | `nx e2e <project>` (builds image, starts real services), `nx serve <project>` (dev infra) |

CI runs `nx affected -t test e2e -c ci`, which mixes tiers 1 and 2.

## Tech Stack

Versions live in `package.json`, `pyproject.toml`, `gradle/libs.versions.toml`, and
`.devcontainer/devcontainer.json` — don't copy them into docs.

- **Monorepo tool**: Nx + Gradle (Java) + uv (Python workspace)
- **Languages**: TypeScript (Angular), Python, Java
- **Frontend**: Angular, SCSS, Storybook, Vitest
- **Backend**: FastAPI, AWS Lambda, Kafka (Confluent), SQLAlchemy/SQLModel
- **Infra**: Docker, Postgres, Keycloak, observability stack (Prometheus/Grafana/Tempo)
- **Quality**: ESLint, Ruff, Prettier, SonarQube, pre-commit hooks
- **Docs**: Zensical (Material design) with mkdocstrings
- **Security**: CycloneDX SBOM, SOPS encryption (per-user age key at `secrets/keys.txt`, never committed)

## Module Map

This is a **removal map**, not a project catalogue: what each project is and
how it is wired lives in its own `AGENTS.md`. It exists because slice
boundaries are a workspace-wide rule — which projects may leave together, and
what to unwire when they do.

The **spine** (keep this): `aurelius-frontend-example`, `aurelius-fastapi-example`,
`libs/python/aurelius-sdk`, `libs/angular/*`, `dev/postgres`, `dev/keycloak`, `dev/observability`,
plus the workflow (CI, pre-commit, SBOM, docs, release).

**Optional slices** (each owns its infra project and env keys; removable together with it):

| Slice           | Projects                                                                                                                                           | Infra                                          |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Kafka streaming | `aurelius-java-producer-example`, `aurelius-node-red-example`, `libs/python/aurelius-kafka`, `connectors/aurelius-kafka-connect-jdbc-sink-example` | `dev/kafka`                                    |
| AWS Lambda      | `aurelius-aws-lambda-example`, `libs/python/aurelius-aws-lambda`                                                                                   | `dev/kafka`, `docker/aurelius-aws-lambda-base` |

When removing a slice, update all of: root `pyproject.toml` (uv members, dev groups, uv.sources),
`settings.gradle.kts`, `implicitDependencies`/`dependsOn` in `project.json` files, `.env` keys,
and the `mkdocs.yaml` nav.

## Key Conventions

- **Nx projects**: Each app/lib has a `project.json`. Use `nx <target> <project>` for builds, tests, lint.
- **Python**: Uses `pyproject.toml` per package. venv at root `.venv/`. Ruff for lint/format, pytest for tests.
- **Java**: Gradle with `settings.gradle.kts`. JDK via foojay-resolver.
- **TypeScript**: ESLint + Prettier. Angular libraries use ng-packagr for publishing.
- **Pre-commit**: Runs Prettier, ESLint, Ruff on all files. Always commit through pre-commit.
- **Schemas**: Avro schemas in `schemas/avro/`. Pydantic-avro for serialization.
- **Release**: Nx release with changelog generation (conventional commits).
- **SonarQube**: Analysis configured per app via `sonar-project.properties`.
- **Secrets**: Real secrets live in per-project `.env.enc` (SOPS). Plaintext `.env` files hold
  dev defaults only. The age key is generated per developer on first devcontainer start.

## Common Commands

```bash
# Build
nx run <project>:build
./gradlew build          # Java

# Test
nx run <project>:test
pytest                   # Python
npx nx test <project>    # TypeScript

# Lint
nx run <project>:lint
pre-commit run --all-files

# Dev server (starts its own infra dependencies)
npx nx serve <project>
uv run zensical serve

# Docker (per-project compose, e.g.)
docker compose -f dev/kafka/docker-compose.yaml up -d
```

## Project Instructions

Every project directory contains a colocated `AGENTS.md` with its wiring,
commands, and removal notes, plus a `README.md` describing what it does.
Read the pair closest to the files you are editing; directory-level
`AGENTS.md` files (e.g. `libs/python/AGENTS.md`, `libs/angular/AGENTS.md`)
hold recipes for adding new projects there. Each project documents itself —
do not add central lists of projects or libraries to this file.

## Code Quality & Testing

### Code Quality

- **Always run linters and type checkers** after making changes — do not assume they pass.
    - TypeScript/JavaScript: `nx run <project>:lint` (ESLint)
    - Python: `ruff check` / `ruff format`
    - Java: Gradle check tasks
    - Markdown: markdownlint
    - SonarQube: code quality and security analysis
- **Never commit code that fails lint or tests** — pre-commit hooks will block it anyway.
- When modifying code, consider the impact on:
    - Type safety (TypeScript strict mode, Python type hints)
    - Linting rules (ESLint, Ruff)
    - Existing test coverage (add tests for new logic)
- For Python, prefer `pyright` for type checking.
- For TypeScript, prefer `tsc --noEmit` for type checking.

### Unit Tests

- **TypeScript/Angular**: Vitest (configured via `@nx/vite` /
  `@nx/vitest`). Test files use `.spec.ts` extension and live
  alongside source files (analog pattern). Run with
  `nx run <project>:test`.
- **Python**: pytest with `pytest-asyncio` for async tests. Test
  files use `test__*.py` convention. Run with `pytest` or
  `nx run <project>:test`.
- **Java**: JUnit 5 via Gradle. Run with `./gradlew test` or
  `nx run <project>:test`.

### End-to-End Tests

- **Frontend**: Playwright (configured via `@nx/playwright`).
  Tests live in `e2e/` directory. Run with `nx run <project>:e2e`.
- **Backend**: pytest-based E2E tests using `testcontainers` for
  spinning up Postgres, Kafka, Keycloak, etc. Run with
  `nx run <project>:e2e`.

### Test Conventions

- **Always use the `ci` configuration** when running Nx test tasks to avoid watch mode and generate coverage reports.
  Watch mode keeps the process running indefinitely and blocks the terminal.
    - Correct: `nx run <project>:test -c ci`
    - Correct: `npx nx test <project> -c ci`
    - **Never** run `nx run <project>:test` without the `ci` configuration — it will hang in watch mode.
- For Python tests, use `pytest` directly.
- For Java tests, use `./gradlew test`.
- Add tests for new logic — do not leave untested code paths.
- For Python async tests, use `pytest-asyncio` with `@pytest.mark.asyncio`.
- For backend E2E, prefer `testcontainers` over mocking infrastructure.
- For frontend E2E, use Playwright's page object model and fixtures.
- Test files should be co-located with source files (analog pattern) where possible.

<!-- nx configuration start-->
<!-- markdownlint-disable -->

## General Guidelines for working with Nx

- For navigating/exploring the workspace, invoke the `nx-workspace` skill first - it has patterns for querying projects, targets, and dependencies
- When running tasks (for example build, lint, test, e2e, etc.), always prefer running the task through `nx` (i.e. `nx run`, `nx run-many`, `nx affected`) instead of using the underlying tooling directly
- Prefix nx commands with the workspace's package manager (e.g., `pnpm nx build`, `npm exec nx test`) - avoids using globally installed CLI
- You have access to the Nx MCP server and its tools, use them to help the user
- For Nx plugin best practices, check `node_modules/@nx/<plugin>/PLUGIN.md`. Not all plugins have this file - proceed without it if unavailable.
- NEVER guess CLI flags - always check nx_docs or `--help` first when unsure

## Scaffolding & Generators

- For scaffolding tasks (creating apps, libs, project structure, setup), ALWAYS invoke the `nx-generate` skill FIRST before exploring or calling MCP tools

## When to use nx_docs

- USE for: advanced config options, unfamiliar flags, migration guides, plugin configuration, edge cases
- DON'T USE for: basic generator syntax (`nx g @nx/react:app`), standard commands, things you already know
- The `nx-generate` skill handles generator discovery internally - don't call nx_docs just to look up generator syntax

<!-- markdownlint-enable -->
<!-- nx configuration end-->
