# Design Log

Technical decisions made during the conversion that are too implementation-specific for an ADR
but must not be lost: storage layout, identifiers, query translation, test tooling. Business-level
decisions are ADRs in [Architecture Decisions](../adr/index.md).

## Rules

- Entries are numbered `DD-NNN`, consecutively; numbers are never reused.
- Statuses: **Proposed** → **Accepted**, then optionally **Superseded by DD-NNN**.
- An accepted entry is never edited except its status line. A changed decision is a new entry
  that supersedes the old one.
- Every entry names the increment that introduced it, so the reasoning can be found next to the
  code and the specification it belongs to.
- An increment that makes a decision adds its entry in the same pull request.

## Entry template

```markdown
### DD-NNN. Decision as a statement

- **Status:** Proposed | Accepted | Superseded by DD-NNN
- **Increment:** N.N
- **Date:** YYYY-MM-DD

**Decision.** What we do, in one or two sentences.

**Reason.** Why, in terms of the requirements of the increment.

**Alternatives.** What else was considered and why it lost.

**Consequences.** What follows, including what must be revisited and when.
```

## Log

| #                                                                              | Decision                                                                  | Increment | Status   |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | --------- | -------- |
| [DD-001](#dd-001-reference-is-apache-atlas-240-and-both-dashboards-are-served) | The reference is Apache Atlas 2.4.0; both dashboards are served unchanged | 0.1       | Accepted |
| [DD-002](#dd-002-atlas-code-lives-in-aurelius-atlas-projects-split-by-layer)   | Atlas code lives in `aurelius-atlas-*` projects split by layer            | 0.1       | Accepted |
| [DD-003](#dd-003-development-nodes-run-with-security-on-and-tls-off)           | Development and test nodes run with security on and TLS off               | 0.2       | Accepted |
| [DD-004](#dd-004-every-index-is-named-prefix-kind)                             | Every index is named `<prefix>-<kind>`                                    | 0.2       | Accepted |
| [DD-005](#dd-005-the-store-uses-the-asynchronous-client)                       | The store uses the asynchronous Elasticsearch client                      | 0.2       | Accepted |
| [DD-006](#dd-006-what-must-be-named-by-a-test)                                 | What must be named by a test, and how a test names it                     | 0.3       | Accepted |
| [DD-007](#dd-007-the-test-report-is-a-ci-artifact-with-a-job-summary)          | The test report is a CI artifact with a job summary                       | 0.3       | Accepted |

### DD-001. Reference is Apache Atlas 2.4.0, and both dashboards are served

- **Status:** Accepted
- **Increment:** 0.1
- **Date:** 2026-10-09

**Decision.** The behaviour to reproduce is that of the `release-2.4.0` tag of Apache Atlas. Both of
its user interfaces are served unchanged at the paths Atlas uses: `dashboardv2` at `/` and
`dashboardv3` at `/n/`. End-to-end tests cover `dashboardv3` in depth and `dashboardv2` with a smoke
test.

**Reason.** Parity tests need one fixed reference ([ADR 048](../adr/048-behaviour-is-proven-against-the-reference-before-it-is-accepted.md)),
and 2.4.0 is the latest Apache Atlas release. Atlas 2.4.0 serves the classic interface at the root and
the newer one under `/n/`, and each links to the other; serving both keeps every bookmark and link
working at the cost of one more static build, whereas dropping one would be a visible deviation.

**Alternatives.** Track Atlas `master`: unstable fixtures, no released artefact to compare against.
Serve only `dashboardv3` and redirect `/` to `/n/`: one build less, but breaks the switch-back link and
existing bookmarks, and would need a deviation entry.

**Consequences.** A move to a later Atlas release is a new entry plus a re-recording of all fixtures.
Features used only by `dashboardv2` still need backend support; they are found by its smoke test.

### DD-002. Atlas code lives in aurelius-atlas projects split by layer

- **Status:** Accepted
- **Increment:** 0.1
- **Date:** 2026-10-09

**Decision.** Atlas code is split into workspace projects by layer, all prefixed `aurelius-atlas-`
(Python packages `aurelius_atlas_*`): `-model` (data shapes, no I/O), `-typesystem` (type registry and
validation), `-store-es` (Elasticsearch access), `-core` (stores and services), `-dsl` (query language),
`apps/aurelius-atlas-server` (REST), `apps/aurelius-atlas-dashboard` (UI),
`reports/aurelius-atlas-test-report`, plus `dev/elasticsearch` and `dev/atlas-reference`.

**Reason.** Layers that do not do I/O can be unit-tested without infrastructure; the dependency
direction (model ← typesystem ← core → store-es; server → core) keeps each increment's change local,
and each project follows an existing template recipe. The `aurelius` prefix keeps the organisation's
naming convention.

**Alternatives.** One large package mirroring the Java module tree: simpler imports, but every change
touches the same project and nothing can be tested in isolation. A package per Java module (`intg`,
`repository`, `webapp`): mirrors history rather than the dependency structure we want.

**Consequences.** Projects are created by the increment that first needs them, not up front.

### DD-003. Development nodes run with security on and TLS off

- **Status:** Accepted
- **Increment:** 0.2
- **Date:** 2026-10-09

**Decision.** The dev node (`dev/elasticsearch`) and the component-test node run single-node with
`xpack.security.enabled=true` (basic auth as `elastic`), HTTP and transport TLS off, and the disk
allocation threshold off. Test start-up waits for a green cluster and three consecutive successful
authentications.

**Reason.** Security on keeps authentication paths (credentials, HTTP 401 handling) exercised from day
one, as in production. TLS on a single local node adds certificate handling to every developer setup
without testing anything we ship. Developer machines are often above Elasticsearch's 90% disk watermark,
which silently leaves the security index unallocated so every login fails. Right after start-up the
`elastic` user switches from the bootstrap password to the security index; requests in that window can
fail with HTTP 401, which made component tests flaky until the readiness wait covered it.

**Alternatives.** Security off in development: simpler, but authentication bugs would first appear in
deployment. Full TLS with generated certificates: realistic but heavy for every developer and CI run.

**Consequences.** These settings must never reach a deployment configuration; the deployment settings
are decided with increment 6.4. Settings in `aurelius_atlas_store_es.testing.container_environment`
and `dev/elasticsearch/docker-compose.yaml` must stay identical.

### DD-004. Every index is named prefix-kind

- **Status:** Accepted
- **Increment:** 0.2
- **Date:** 2026-10-09

**Decision.** Every index this system creates is named `<index_prefix>-<kind>` through
`aurelius_atlas_store_es.indices.index_name`; the prefix defaults to `atlas`, kinds are lower-case
snake case.

**Reason.** A configurable prefix lets several installations or test runs share one cluster and lets
operators grant privileges by pattern (`atlas-*`). One function owning the rule means no module
invents its own names.

**Alternatives.** Fixed names: simplest, but test isolation and shared clusters become impossible.
Data streams: designed for append-only time series, a fit for audit events only; can be adopted for
that kind later without changing the rule for the others.

**Consequences.** Index kinds are introduced by the increments that need them, each with its mapping
recorded in a design-log entry.

### DD-005. The store uses the asynchronous client

- **Status:** Accepted
- **Increment:** 0.2
- **Date:** 2026-10-09

**Decision.** All Elasticsearch access uses `AsyncElasticsearch` (with its aiohttp transport); store
functions are `async`.

**Reason.** The server is FastAPI, which serves requests on an event loop; synchronous I/O there blocks
every concurrent request. Lineage and propagation (increments 3.4, 5.1) issue many queries per request
and benefit from concurrency.

**Alternatives.** The synchronous client in a thread pool: works, but hides blocking behind threads
and makes concurrency limits harder to reason about.

**Consequences.** Store and service code is async end to end; command-line tools call it with
`asyncio.run`.

### DD-006. What must be named by a test

- **Status:** Accepted
- **Increment:** 0.3
- **Date:** 2026-10-09

**Decision.** In every project matched by `[tool.aurelius-atlas.traceability] projects`, these must be
named by a `@pytest.mark.covers("<dotted path>")` test: public module-level functions, public methods
and properties of public classes, and classes whose only behaviour is private (for example a model
with private validators). Pure data classes and exceptions without methods, private names, private
modules and `__main__` are not listed. A target names an item when it equals the item's path; a class
item is also named by targets inside it. The inventory is read from source with `ast`, never by
importing. The covers declarations are read by collecting the tests (`pytest --collect-only`), so the
check sees every project, not only the ones a CI run touched.

**Reason.** ADR 049 asks for every function; data-only classes have no behaviour of their own, and
requiring a test for each would create tests that only construct objects. Reading source with `ast`
avoids import side effects and works for projects whose dependencies are not importable together.
Collecting instead of running makes the check complete and takes seconds.

**Alternatives.** Static parsing of test files for markers: no pytest needed, but cannot resolve
targets held in constants or f-strings, which tests use to stay readable. Coverage-based (any line of
the function executed): counts incidental execution, which is what ADR 049 rejects.

**Consequences.** Adding a public function without a naming test fails CI. A test may name several
functions with several markers. The plugin is loaded through the `pytest11` entry point; the
`aurelius-atlas-testing` project itself loads it from its `conftest.py` instead so coverage measures
the plugin's own import.

### DD-007. The test report is a CI artifact with a job summary

- **Status:** Accepted
- **Increment:** 0.3
- **Date:** 2026-10-09

**Decision.** CI renders the report after the tests on every run (also when they fail), uploads
`reports/aurelius-atlas-test-report/dist/` as the `test-report` artifact, and appends the Markdown
summary to the job summary, which GitHub shows on the run and the pull request checks.

**Reason.** The report must exist for every change, including failing ones, and must be one click
from the pull request. The docs site is published by a separate workflow that does not run tests;
coupling it to test results would either rerun all tests or pass artifacts between workflows.

**Alternatives.** Publishing the report on the per-PR docs site: nicer URL, but needs a cross-workflow
artifact hand-over or a second full test run. A PR comment bot: visible, but posts on every push and
needs write permissions.

**Consequences.** The report covers the projects the run tested (`nx affected`); traceability always
covers all projects because the check collects them. Comparison with `main` over time and docs-site
publishing remain open; revisit when the parity suite makes runs long enough for trends to matter.
