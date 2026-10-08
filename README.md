# Aurelius Project Template

A polyglot monorepo template for enterprise microservice projects: a working reference architecture,
running examples, and the delivery workflow (CI, quality gates, SBOM, docs, release) that surrounds them.
It is designed to be forked, renamed, and stripped down to the slices your project actually needs.

| Layer    | Technology                                                    |
| -------- | ------------------------------------------------------------- |
| Monorepo | Nx, uv (Python workspace), Gradle (Java)                      |
| Frontend | Angular, SCSS, Storybook, Vitest                              |
| Backend  | Python (FastAPI, AWS Lambda), Java (Kafka producer)           |
| Data     | Kafka + Schema Registry (Avro), Postgres, SQLAlchemy/SQLModel |
| Infra    | Docker Compose, Keycloak, Prometheus/Grafana/Tempo/Loki       |
| Quality  | ESLint, Ruff, pyright, Prettier, SonarQube, pre-commit        |
| Security | SOPS-encrypted secrets, CycloneDX SBOM, cosign signing        |
| Docs     | Zensical with per-project API references                      |

All toolchain versions are pinned in the development container and the dependency manifests — there is
nothing to install by hand beyond Docker and VS Code.

## Quickstart

1. Install [Docker](https://www.docker.com) and the VS Code
   [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack),
   then clone this repository and open it in VS Code.
2. Choose **Reopen in Container** when prompted. The first build installs the full toolchain and can take
   a while; it also generates your personal secrets key into `secrets/keys.txt`.
3. Register your secrets key (see [Secrets Management](docs/contributor-guide/secrets-management.md)) —
   until you do, test and serve commands fail at the decryption step.
4. Run an example:

    ```bash
    npx nx serve aurelius-fastapi-example
    ```

    Development infrastructure (Keycloak, Postgres, observability) starts automatically.

5. Verify your setup:

    ```bash
    nx test aurelius-fastapi-example -c ci
    ```

??? WARNING "First-run expectations"

    - Every `serve`/`test`/`e2e` target first decrypts the project's `.env.enc` secrets; without a
      registered key you get a SOPS/age decryption error, not a code failure.
    - Unit tests need only that decryption; `e2e` targets additionally build Docker images and start real
      services (Postgres, Kafka, Keycloak), so they need the container runtime.
    - Always pass `-c ci` to test targets — without it they run in watch mode and never exit.

## What is in the box

The repository is a monorepo of small, removable slices: an Angular frontend, a FastAPI backend, an AWS
Lambda consumer, a Java Kafka producer, a Node-RED flow, and a Kafka Connect sink — all exchanging one
shared Avro event, backed by local development infrastructure (Postgres, Keycloak, Kafka, observability).
The [Development Environment](docs/contributor-guide/development-environment.md) guide walks through the
directory layout, and `npx nx graph` visualizes how the projects fit together.

## Adopting this template for your project

Fork, then work through the
[Adopting the Template](docs/contributor-guide/adopting-the-template.md) guide: it is the rename checklist
for every hardcoded identity in the repository and the runbook for re-founding the secrets trust with your
own team's keys. Example slices you do not need can be removed as whole units — each project directory
documents its own removal steps.

## Documentation

The full documentation site (user guide, contributor guide, architecture decisions) is published from
[`mkdocs.yaml`](mkdocs.yaml); build and preview it locally with:

```bash
uv run zensical serve
```

For AI coding agents, the repository carries colocated instruction files (`AGENTS.md`) in every project
directory.
