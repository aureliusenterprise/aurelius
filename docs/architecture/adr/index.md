# Architecture Decisions

This section records architecture decisions as Architecture Decision Records
(ADRs): short documents that capture a decision, the business situation that
forced it, and the consequences it has. Code tells you _what_ was built; an ADR
tells you _why_ — and the _why_ is the part code cannot hand over.

## The decision log

New here? This is the whole set in one table. Read the records that govern the
area you are about to work in; the rest can wait.

| #                                                                                    | Decision                                                                                                                               | Status   |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [001](./001-single-monorepo.md)                                                      | Keep one monorepo for every stack — one repository, one entry point, atomic cross-stack change.                                        | Accepted |
| [002](./002-modules-are-removable-slices.md)                                         | Modules are removable as whole slices — spine or optional capability, deleted in one pass.                                             | Accepted |
| [003](./003-every-project-documents-itself.md)                                       | Every project documents itself — knowledge beside what it describes, no central catalogue.                                             | Accepted |
| [004](./004-one-shared-domain-model.md)                                              | One shared domain model — one canonical definition per concept, generated or checked everywhere.                                       | Accepted |
| [005](./005-dev-infra-starts-with-the-app.md)                                        | Development infrastructure starts with the app — one command to a running system.                                                      | Accepted |
| [006](./006-the-whole-system-runs-on-one-machine.md)                                 | The whole system runs on one machine — defects reproducible locally, validation without operated infrastructure.                       | Accepted |
| [007](./007-one-shared-identity-provider.md)                                         | One shared identity provider — one place people exist; surfaces only verify what it issues.                                            | Accepted |
| [008](./008-secrets-never-in-plaintext.md)                                           | Real secrets encrypted, dev defaults committed — ciphertext travels with the code.                                                     | Accepted |
| [009](./009-examples-must-run-and-be-tested.md)                                      | Every example runs and is tested — a broken example is removed, not annotated.                                                         | Accepted |
| [010](./010-the-unit-validated-is-the-unit-that-ships.md)                            | The unit validated is the unit that ships — one build per change, environments differ by settings only.                                | Accepted |
| [011](./011-the-development-environment-is-a-versioned-artifact.md)                  | The development environment is a versioned artifact — one base for people and pipelines.                                               | Accepted |
| [012](./012-validation-runs-against-real-services.md)                                | Validation runs against real services — a passing test is evidence about the shipped path.                                             | Accepted |
| [013](./013-services-prove-who-they-are-at-every-boundary.md)                        | Services prove who they are at every boundary — machine identity, separate from human identity.                                        | Accepted |
| [014](./014-the-gate-is-defined-once-and-runs-everywhere.md)                         | The gate is defined once — the same rule set runs at commit time and in the pipeline.                                                  | Accepted |
| [015](./015-a-change-answers-for-what-it-caused.md)                                  | A change answers for what it caused — change-caused findings block; world-state findings are reviewed on a cadence.                    | Accepted |
| [016](./016-the-system-observes-itself-internally.md)                                | The system observes itself — traces, metrics, and logs never leave the boundary.                                                       | Accepted |
| [017](./017-shared-concepts-change-only-compatibly.md)                               | Shared concepts change only compatibly — additive by default, a breaking change becomes a new version.                                 | Accepted |
| [018](./018-settings-arrive-at-startup-through-one-channel.md)                       | Settings arrive at startup through one channel — read once, validated, failing loudly.                                                 | Accepted |
| [019](./019-the-system-releases-as-one-versioned-whole.md)                           | The system releases as one versioned whole — one number, one changelog, one release event.                                             | Accepted |
| [020](./020-dependencies-stay-current-by-default.md)                                 | Dependencies stay current by default — routine updates automatic, framework majors planned.                                            | Accepted |
| [021](./021-a-new-technology-joins-by-recipe.md)                                     | A new technology joins by recipe — discovered, gated, releasable, removable in one pass.                                               | Accepted |
| [022](./022-the-codebase-explains-itself-to-its-agents.md)                           | The codebase explains itself to its agents — nearest-first instructions for machine readers.                                           | Accepted |
| [023](./023-storage-schema-changes-by-recorded-migration.md)                         | A storage schema changes only by recorded migration — one ordered path, data moved rather than replaced.                               | Proposed |
| [024](./024-a-validated-release-is-promoted-by-a-declared-path.md)                   | A validated release is promoted by a declared path — dev and test are the system's; beyond that, the deployment's.                     | Accepted |
| [025](./025-data-has-a-stated-lifetime.md)                                           | Data has a stated lifetime — every kind expires on a named schedule the system enforces.                                               | Proposed |
| [026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md)                 | The system can be brought back from a named snapshot — backups stated, recovery rehearsed, loss bounded.                               | Proposed |
| [027](./027-every-stream-carries-a-stated-delivery-guarantee.md)                     | Every stream carries a stated delivery guarantee — duplication and loss decided per stream, not defaulted.                             | Proposed |
| [028](./028-operational-secret-handling-has-a-named-owner.md)                        | Operational secret handling has a named owner — rotation, loss, and break-glass rehearsed, not invented.                               | Proposed |
| [029](./029-shipped-artifacts-are-signed-and-their-origin-is-provable.md)            | What ships is signed and its origin provable — verification is part of delivery, not a later hope.                                     | Accepted |
| [030](./030-interfaces-between-parts-are-verified-not-assumed.md)                    | Interfaces between parts are verified, not assumed — the agreement is stated once and drift fails the change.                          | Proposed |
| [031](./031-runtime-versions-have-a-declared-support-window.md)                      | Runtime versions have a declared support window — one answer per runtime, bumps planned, nothing floating.                             | Proposed |
| [032](./032-shared-streams-are-named-by-a-declared-convention.md)                    | Shared streams are named by a declared convention — the name says what flows and which version, never where.                           | Accepted |
| [033](./033-shipped-artifacts-carry-a-contents-inventory.md)                         | Shipped artifacts carry a contents inventory — what is in what we ran is a lookup, not a reconstruction.                               | Accepted |
| [034](./034-signals-meet-at-one-replaceable-collection-point.md)                     | Signals meet at one replaceable collection point — parts export to a seam, never to a backend directly.                                | Accepted |
| [035](./035-parts-hand-work-through-a-durable-event-log.md)                          | Parts hand work through a durable event log — the log is the default integration; joining is a subscription.                           | Accepted |
| [036](./036-the-delivery-plane-is-a-named-exception-to-the-data-boundary.md)         | The delivery plane is a named exception to the data boundary — the pipeline crosses at recorded points; the running system never does. | Accepted |
| [037](./037-the-system-itself-promises-nothing-about-staying-up.md)                  | The system itself promises nothing about staying up — availability is what the deployment builds around it.                            | Accepted |
| [038](./038-what-a-person-may-do-is-decided-in-one-place-apart-from-who-they-are.md) | What a person may do is decided in one place — permission apart from identity; one answer, one act to revoke.                          | Proposed |
| [039](./039-data-is-protected-where-it-travels-and-where-it-rests.md)                | Data is protected where it travels and rests — declared arrangements, not assumed properties.                                          | Proposed |
| [040](./040-the-system-raises-its-hand-when-it-is-broken.md)                         | The system raises its hand when it is broken — named triggers, named destinations; silence is a condition.                             | Proposed |
| [041](./041-a-failure-of-the-running-system-has-an-owner-and-a-rehearsed-path.md)    | A failure of the running system has an owner and a rehearsed path — response owned, written, practised.                                | Proposed |
| [042](./042-every-dataset-has-an-owner-who-answers-for-it.md)                        | Every dataset has an owner who answers for it — sharing is a stated answer, never an absence.                                          | Proposed |

## Why record decisions

- **Decisions are inherited.** Every codebase is read first by people who were
  not in the room — onboarding, handover, a fork. Without the reasoning, they
  cannot tell a deliberate constraint from an accident, and will "fix"
  decisions that were the whole point.
- **Decisions outlive implementations.** Frameworks and libraries change; the
  business reasoning behind a modular, removable design does not.
- **New contributors get the context.** An ADR gives a reader the reasoning
  behind the wiring, so they can tell when a change would contradict an
  accepted decision.
- **Review has a reference.** A pull request that quietly reverses an accepted
  decision is visible the moment it contradicts an ADR.

## Keep decisions business-focused

An ADR records a decision that **constrains or enables business capabilities**.
Implementation detail — how a library is configured, which version of a
framework is pinned — belongs in code and project documentation, not here.

!!! TIP "The litmus test"

    Would this decision still matter if we replaced every technology in the
    stack? If yes, it is an ADR. If no, it is an implementation detail.

| ADR material                                                            | Not ADR material                      |
| ----------------------------------------------------------------------- | ------------------------------------- |
| One shared domain model serves streaming and storage                    | How pydantic-avro serialises a record |
| Modules must be removable as whole slices                               | Nx plugin configuration               |
| Real secrets are encrypted per project; only dev defaults are committed | SOPS command-line flags               |
| Development infrastructure starts with the app that needs it            | Docker Compose syntax                 |
| Every project documents itself; no central catalogues                   | MkDocs navigation entries             |

Write the **Context** as a business situation (cost, risk, time-to-market,
team autonomy, compliance), not as a technology comparison. Technologies may
appear as evidence, but the drivers must stand without them.

State the **Decision** as a property that now holds, and name the current
implementation only under **Neutral / follow-ups**. A record titled with a
technology goes stale when the technology is replaced; a record titled with a
property survives the replacement and says what replaced it.

## Lifecycle

- Number records `NNN-short-slug` (e.g. `001-single-monorepo.md`); numbers
  are never reused.
- Statuses: **Proposed** → **Accepted**, then optionally **Superseded** (by a
  later record) or **Deprecated**.
- **Accepted** means the decision is made and the mechanism that makes it
  true exists in the spine of the system. A single part or stack that
  deviates is a named deviation: it belongs in the record's follow-ups and
  does not by itself block acceptance. **Proposed** means the decision is
  not yet made, or the mechanism does not yet exist where it must. The test
  is where the mechanism lives, not how uniformly it is used: a part that
  skips an existing mechanism is a named deviation under an Accepted record;
  a rule with no enforcement point anywhere is Proposed. A stated convention
  that the parts follow is itself an enforcement point: the record is
  Accepted and a missing automated check is a named gap, not a Proposed
  status.
- Never edit the decision of an accepted record. When the business situation
  changes, write a new record that supersedes it and update the old record's
  status line only.
- When a record is superseded, check the records that cite it: a requirement
  borrowed from a superseded record no longer has a foundation, so the
  dependent record either adopts the requirement in its own words, cites the
  superseding record, or is itself revisited — recorded in a new record, not
  by editing the old decision.
- Add each new record to the `nav` section of `mkdocs.yaml`.

## Using ADRs

- Start the log at `001` and keep the numbering consecutive; the log belongs to
  whoever maintains the codebase.
- State every requirement in the record's own words. A requirement phrased as
  "the property NNN demands" outsources its foundation to another record: if
  that record is superseded, the requirement loses its reason for existing —
  the same failure the supersession rule above guards against, from the
  drafting side.
- Reference the records that govern an area in pull requests touching it and link
  to them from the project documentation they explain.
- Review them occasionally: a record whose consequences no longer hold is a
  signal to write its successor.

## Terms used in these records

The records use a small vocabulary consistently; these notes are the shared
definitions.

- **Spine** — the parts of the codebase that stay no matter which optional
  capabilities are removed: the example apps, shared libraries, and the
  development infrastructure
  ([002](./002-modules-are-removable-slices.md)).
- **Slice** — an optional capability and the infrastructure it owns, removed
  as one unit ([002](./002-modules-are-removable-slices.md)).
- **The gate** — the shared rule set that runs at commit time and in the
  pipeline ([014](./014-the-gate-is-defined-once-and-runs-everywhere.md)).
- **Event platform** — the message system business events flow through
  ([005](./005-dev-infra-starts-with-the-app.md)); where a record speaks of a
  **stream**, it means one of the platform's topics, named by
  [032](./032-shared-streams-are-named-by-a-declared-convention.md) and
  guaranteed per [027](./027-every-stream-carries-a-stated-delivery-guarantee.md).
- **Collection point** — the single seam where parts hand over traces,
  metrics, and logs ([016](./016-the-system-observes-itself-internally.md)).
- **Taught path** — the arrangement an example demonstrates, which a future
  reader will copy ([009](./009-examples-must-run-and-be-tested.md)).
- **Delivery plane** — the pipeline activity that validates and releases the
  system, distinct from the running system; the only place the data boundary
  may be crossed, and only at named points
  ([036](./036-the-delivery-plane-is-a-named-exception-to-the-data-boundary.md)).
- **Dataset owner** — the named role that answers for a dataset's shape,
  lifetime, and quality
  ([042](./042-every-dataset-has-an-owner-who-answers-for-it.md)).

## Gaps with a record but no mechanism yet

Some questions the records lean on were listed here when they had no record at
all. Each now has one, Proposed: the question is framed, the requirements are
written, and the decision — including the numbers and owners those records
defer — is what acceptance adds.

The gaps also sequence the work: taking on real stored data needs the
migration path ([023](./023-storage-schema-changes-by-recorded-migration.md))
and the recovery path
([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md))
first; and credentials cannot honestly claim rotation until operational secret
handling
([028](./028-operational-secret-handling-has-a-named-owner.md)) is decided.

- **Storage schema lifecycle** —
  [023](./023-storage-schema-changes-by-recorded-migration.md), which
  [004](./004-one-shared-domain-model.md) and
  [017](./017-shared-concepts-change-only-compatibly.md) were assumed to
  lean on.
- **Data retention** —
  [025](./025-data-has-a-stated-lifetime.md), inside the boundary
  [016](./016-the-system-observes-itself-internally.md) draws.
- **Recovery** —
  [026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md).
- **Event delivery guarantees** —
  [027](./027-every-stream-carries-a-stated-delivery-guarantee.md), the
  behaviour beside the content that
  [017](./017-shared-concepts-change-only-compatibly.md) does not cover.
- **Operational secret handling** —
  [028](./028-operational-secret-handling-has-a-named-owner.md), the half
  [008](./008-secrets-never-in-plaintext.md) named as nobody's decision.
- **Interface verification** —
  [030](./030-interfaces-between-parts-are-verified-not-assumed.md), the
  standing question [004](./004-one-shared-domain-model.md) left open for
  travelling representations.
- **Runtime support windows** —
  [031](./031-runtime-versions-have-a-declared-support-window.md), what
  [020](./020-dependencies-stay-current-by-default.md) does not speak to.
- **Authorization** —
  [038](./038-what-a-person-may-do-is-decided-in-one-place-apart-from-who-they-are.md),
  the permission question the identity record
  ([007](./007-one-shared-identity-provider.md)) deliberately leaves open.
- **Data protection in transit and at rest** —
  [039](./039-data-is-protected-where-it-travels-and-where-it-rests.md), the
  protection of the data itself that the credential rule
  ([008](./008-secrets-never-in-plaintext.md)) does not cover.
- **Alerting** —
  [040](./040-the-system-raises-its-hand-when-it-is-broken.md), the noticing
  the collection point
  ([034](./034-signals-meet-at-one-replaceable-collection-point.md)) does not
  do by itself.
- **Incident response** —
  [041](./041-a-failure-of-the-running-system-has-an-owner-and-a-rehearsed-path.md),
  the path that begins where
  [040](./040-the-system-raises-its-hand-when-it-is-broken.md)'s announcement
  arrives.
- **Dataset ownership** —
  [042](./042-every-dataset-has-an-owner-who-answers-for-it.md), the answer
  the migration path
  ([023](./023-storage-schema-changes-by-recorded-migration.md)) and the
  lifetimes ([025](./025-data-has-a-stated-lifetime.md)) each need someone to
  give.

A gap is listed here only while its record is Proposed. Accepting a record
moves its status into the log above; finding a new gap means writing a record
for it, not editing the records above.

## Next steps

- Copy the [ADR Template](./template.md) when writing a record.
- This section sits alongside the governance pages under
  [Architecture](../index.md): those describe target-state capabilities, ADRs
  record the decisions that shaped them.
