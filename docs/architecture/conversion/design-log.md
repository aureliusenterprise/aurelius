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
