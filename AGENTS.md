# Workspace Context

This is the **Aurelius Project Template** — a polyglot monorepo for bootstrapping enterprise microservice projects.

## Quick Start

1. **Install dependencies**: `npm ci` (root) + `uv sync` + `./gradlew dependencies` (Java)
2. **Start infrastructure**: `docker compose -f dev/docker-compose.yml up -d`
3. **Activate Python venv**: `source .venv/bin/activate`
4. **Run pre-commit**: `pre-commit run --all-files` (fix any issues)
5. **Verify**: `nx run-many --target=test e2e` (or target a specific app)

> [!NOTE]
> This is a **template** — apps/libs are starting points, not production-ready as-is.

## Tech Stack

- **Monorepo tool**: Nx (v22.7.1) + Gradle (Java)
- **Languages**: TypeScript/JavaScript (Angular 21), Python (3.14+), Java
- **Frontend**: Angular 21, SCSS, Storybook, Vitest
- **Backend**: FastAPI, AWS Lambda, Kafka (Confluent), SQLAlchemy
- **Infra**: Docker, Postgres, Keycloak, observability stack (Prometheus/Grafana/Tempo)
- **Quality**: ESLint, Ruff, Prettier, SonarQube, pre-commit hooks
- **Docs**: MkDocs Material with mkdocstrings
- **Security**: CycloneDX SBOM, SOPS encryption

## Key Conventions

- **Nx projects**: Each app/lib has a `project.json`. Use `nx <target> <project>` for builds, tests, lint.
- **Python**: Uses `pyproject.toml` per package. venv at root `.venv/`. Ruff for lint/format, pytest for tests.
- **Java**: Gradle with `settings.gradle.kts`. JDK via foojay-resolver.
- **TypeScript**: ESLint + Prettier. Angular libraries use ng-packagr for publishing.
- **Pre-commit**: Runs Prettier, ESLint, Ruff on all files. Always commit through pre-commit.
- **Schemas**: Avro schemas in `schemas/avro/`. Pydantic-avro for serialization.
- **Release**: Nx release with changelog generation.
- **SonarQube**: Analysis configured per app via `sonar-project.properties`.

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

# Dev server
npx nx serve <project>
mkdocs serve

# Docker
docker compose -f dev/docker-compose.yml up -d
```

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
