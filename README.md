# Aurelius Atlas

A Python re-implementation of [Apache Atlas](https://atlas.apache.org): the same REST API and the same
dashboard, with Elasticsearch 9 as the only backend instead of JanusGraph, HBase and Solr. The Java
code base is converted in small, reviewed increments, each proven against the reference Java Atlas.

| Layer    | Technology                                                         |
| -------- | ------------------------------------------------------------------ |
| Monorepo | Nx, uv (Python workspace)                                          |
| Frontend | The original Apache Atlas dashboard, served unchanged              |
| Backend  | Python (FastAPI)                                                   |
| Data     | Elasticsearch 9                                                    |
| Infra    | Docker Compose, Keycloak, Prometheus/Grafana/Tempo/Loki            |
| Quality  | Ruff, pyright, Prettier, SonarQube, pre-commit, traceability check |
| Security | SOPS-encrypted secrets, CycloneDX SBOM, cosign signing             |
| Docs     | Zensical with per-project API references                           |

The conversion plan, its increments and every design decision live in
[`docs/architecture/conversion/`](docs/architecture/conversion/index.md). This repository was adopted
from the Aurelius Project Template and keeps its history, so template updates can still be merged.

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
4. Run the server:

    ```bash
    npx nx serve aurelius-atlas-server
    curl http://localhost:21000/api/atlas/admin/version
    ```

    Elasticsearch starts automatically. For the dashboards, see `apps/aurelius-atlas-dashboard/README.md`.

5. Verify your setup:

    ```bash
    nx run-many -t test -c ci
    nx check aurelius-atlas-test-report
    ```

??? WARNING "First-run expectations"

    - Every `serve`/`test`/`e2e` target first decrypts the project's `.env.enc` secrets; without a
      registered key you get a SOPS/age decryption error, not a code failure.
    - Unit tests need only that decryption; `e2e` targets additionally build Docker images and start real
      services (Elasticsearch, Keycloak), so they need the container runtime.
    - Always pass `-c ci` to test targets — without it they run in watch mode and never exit.

## What is in the box

| Project                                                                         | What it is                                                      |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `apps/aurelius-atlas-server`                                                    | The Atlas REST API (FastAPI)                                    |
| `apps/aurelius-atlas-dashboard`                                                 | The Atlas dashboards, built unchanged from the Atlas source tag |
| `libs/python/aurelius-atlas-store-es`                                           | Elasticsearch access                                            |
| `libs/python/aurelius-atlas-parity`                                             | Parity testing against the reference Atlas                      |
| `libs/python/aurelius-atlas-testing`                                            | The `covers` marker and the traceability check                  |
| `reports/aurelius-atlas-test-report`                                            | One HTML page per run: results, traceability, parity, coverage  |
| `dev/elasticsearch`, `dev/keycloak`, `dev/observability`, `dev/atlas-reference` | Development infrastructure                                      |

Each project documents itself in its `README.md` and `AGENTS.md`; `npx nx graph` shows how they fit
together.

## Following the template

Template updates are merged from the `template` remote. The
[Adopting the Template](docs/contributor-guide/adopting-the-template.md) guide records what was renamed
and removed when this repository was created.

## Documentation

The full documentation site (user guide, contributor guide, architecture decisions) is published from
[`mkdocs.yaml`](mkdocs.yaml); build and preview it locally with:

```bash
uv run zensical serve
```

For AI coding agents, the repository carries colocated instruction files (`AGENTS.md`) in every project
directory.
