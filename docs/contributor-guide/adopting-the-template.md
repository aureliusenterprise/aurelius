# Adopting This Template

!!! NOTE "How this repository adopted the template"

    Aurelius Atlas was created from the template on 2026-10-09 by increment 0.1 of the conversion
    (see [Conversion](../architecture/conversion/index.md)). It stays inside the Aurelius Enterprise
    organisation, so the `aurelius` identity and the secrets trust root (Case A below) were kept.
    The Kafka streaming and AWS Lambda slices, the Java libraries and the Gradle build were removed
    ([ADR 050](../architecture/adr/050-the-system-carries-only-what-the-catalogue-needs.md)); the
    repository and docs site were renamed to `aurelius-atlas`. Sections below that name removed
    projects describe the template, not this repository.

This repository is a template: a working reference architecture meant to be forked and renamed for your own
project. This guide is the checklist for that transition — what to rename, how to re-found the secrets trust,
and what to expect on the first run.

??? INFO "Removing example slices instead of renaming"

    The example applications are designed to be removed as whole slices (for example, the Kafka streaming or
    AWS Lambda slices). Each project directory documents its own removal steps; see the module map in the
    repository root for which projects may leave together.

## Rename Checklist

The template carries the `aurelius` / `aureliusenterprise` identity in places that are **not** generated —
they must be edited by hand. Work through this list top to bottom; each item names concrete files.

### 1. Repository identity

| Surface                        | Files to edit                                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Docs site name, URL, repo link | `mkdocs.yaml` (`site_name`, `site_url`, `repo_url`, `repo_name`, `copyright`)                                      |
| Clone URL in setup guide       | `docs/contributor-guide/development-environment.md`                                                                |
| Bot identity in CI             | `.github/workflows/publish-docs-*.yaml`, `rotate-keys.yaml`, `unpublish-docs.yaml` (`info@aureliusenterprise.com`) |
| Release verification identity  | `.github/workflows/publish.yaml` — the `--identity` regex hardcodes the repository name                            |
| Root package names             | `package.json` and `pyproject.toml` (`name = "aurelius-project-template"`, author entries)                         |

### 2. Project names and directories

Every project under `apps/`, `libs/`, `connectors/`, `dev/`, `docker/`, and `reports/` carries the
`aurelius-` prefix in its directory name, its `project.json` `name`, and its package manifest
(`package.json` / `pyproject.toml` / Gradle project). Renaming a project means updating **all** of:

- The directory itself and every path reference to it.
- `project.json` (`name`, `implicitDependencies`, `dependsOn`) — and every _other_ project that references it.
- Root wiring: `pyproject.toml` (uv members, dev groups, `[tool.uv.sources]`), `settings.gradle.kts`
  (Java modules), `package.json` (`file:` dependencies), `tsconfig.base.json` (`paths`).
- `mkdocs.yaml` nav entries and `docs/api-reference/` page paths.
- ESLint config `prefix` values in per-project `eslint.config.mjs` files.
- Compose project/network names in `dev/**/docker-compose.yaml` and `apps/*/e2e/docker-compose.yaml`.

??? TIP "Check your work with Nx"

    After renaming, `npx nx reset` followed by `npx nx show projects` should list every project without
    graph errors. A stale reference anywhere breaks the graph immediately.

### 3. Python package names

Python packages use underscored names derived from the project (`aurelius_fastapi_example`, `aurelius_sdk`,
`aurelius_example`, `aurelius_kafka`, `aurelius_aws_lambda`). Renaming a package means renaming its
directory, the `name` and `packages` fields in its `pyproject.toml`, and **every import** across apps,
libs, and `e2e/` test modules.

### 4. Java packages and the Avro namespace

- Java sources live under `com.aureliusenterprise.*` (`apps/aurelius-java-producer-example/src/...`,
  `libs/java/aurelius-java-example/src/...`). Rename the package directories, every `package` statement,
  the `mainClass` in `build.gradle.kts`, and the `CMD` in `apps/aurelius-java-producer-example/Dockerfile`.
- The shared schema lives at `schemas/avro/com/aureliusenterprise/example/Entity.avsc`; its `namespace`
  is the Avro **subject** (`com.aureliusenterprise.example.Entity`) seen by every producer and consumer.
  Changing it is a breaking change for any stream you keep.
- The subject string is repeated in: `apps/aurelius-node-red-example/.env` and `flows.json`, the Lambda
  handler (`apps/aurelius-aws-lambda-example/aurelius_aws_lambda_example/handler.py`), the Java producer
  config (`SERIALIZABLE_PACKAGES`), the connector config, and every `e2e/conftest.py`.

??? WARNING "flows.json embeds the whole schema"

    `apps/aurelius-node-red-example/flows.json` contains the full Avro schema inline (the Kafka node's
    `autoSchema` field). Do not hand-edit it; open the flow in the Node-RED editor and re-export after
    changing the schema or subject.

### 5. Angular library aliases

The Angular libraries are imported by **bare names** declared in `tsconfig.base.json` (`aurelius-ui`,
`aurelius-data-access`, `aurelius-observability`) — not under an `@scope/`. Only `@aurelius/brand`
(`libs/styles/aurelius-brand`, a `file:` npm dependency used in SCSS as `@use "@aurelius/brand/src/main"`)
is scoped. Rename the aliases, the import statements, the package `name` fields, and the brand package
together.

### 6. Container registry namespace

The image namespace `ghcr.io/aureliusenterprise` is **hardcoded in plugin code**:
`tools/plugins/docker.ts` (six target definitions). Edit it there, then update the `:local` image
references in the `e2e/docker-compose.yaml` files and the connector's `docker-compose.yaml`, plus the
`org.opencontainers.image.source` labels in the Dockerfiles.

### 7. SonarQube organization

Each analyzed app has `sonar.organization=aureliusenterprise` and `sonar.projectKey=aurelius-*` in its
`sonar-project.properties`. Point these at your SonarCloud organization (or disable the `sonar` step in CI
until your projects exist there).

### 8. Keycloak realm and clients

The development realm import (`dev/keycloak/import/master.json`) defines a client with id `aurelius`.
Rename it there and in both consumers: `apps/aurelius-frontend-example/dev/config.json` and
`apps/aurelius-frontend-example/e2e/config/config.json` (`clientId`).

### 9. Documentation references

After the code renames, sweep the prose: project READMEs, `docs/api-reference/`, and the design guide all
name example projects and the Avro subject. `zensical build --strict` will catch broken nav, but not stale
names in text.

## Re-founding the Secrets Trust

Secrets are committed as SOPS-encrypted `.env.enc` files. They are encrypted for a specific list of age
public keys in `.sops.yaml` — the **trust root**. A fork inherits the template authors' keys, not yours, so
nothing decrypts until you re-found it.

??? WARNING "Symptom of an un-founded fork"

    On a fresh clone, `nx test`, `nx serve`, and `nx e2e` fail with a SOPS/age decryption error. Almost every
    run target first runs `decrypt`, which needs a private key matching a public key in `.sops.yaml`. This is
    expected on a fork — not a broken setup.

### Case A: Joining the existing organization

If you are joining the team that owns the repository, follow
[Registering a new key pair](./secrets-management.md#registering-a-new-key-pair): add your public key to
`.sops.yaml`, open a pull request, and let the key-rotation workflow re-encrypt the files for you.

### Case B: Forking to a new team (no old key available)

When the old team's private keys are not (or should no longer be) in play, re-found the trust root by hand:

1. Generate a key pair for each developer (automatic on first devcontainer start, or via `nx keygen`).
2. Replace the entire `age:` list in `.sops.yaml` with the new team's public keys.
3. The old `.env.enc` files can no longer be decrypted. Recreate the plaintext `.env` files from the
   values your team uses (dev defaults are documented in each project's README and settings model), then
   run the `encrypt` target for each project to re-encrypt them under the new key list:

    ```bash
    nx encrypt <project-name>
    ```

4. Commit the new `.sops.yaml` and the re-encrypted `.env.enc` files together, and confirm a teammate can
   run `nx decrypt <project-name>` before merging.
5. Delete the stale plaintext `.env` files afterwards — they are gitignored, but leaving them around hides
   decrypt failures.

!!! DANGER "Rotate any real values"

    If any `.env.enc` file ever held real (non-dev) credentials shared with the old key list, treat those
    values as exposed to the previous recipients and rotate them.

## First-Run Expectations

- The first devcontainer build installs the full pinned toolchain and can take a while; subsequent starts
  are cached.
- `npm install` and `uv sync` run automatically during container creation; so does age key generation into
  `secrets/keys.txt`.
- Until your key is registered (Case A) or the trust is re-founded (Case B), test and serve targets fail at
  the `decrypt` step.
- Unit tests need only decryption; `e2e` targets additionally build Docker images and start real services,
  so they need the container runtime available.
