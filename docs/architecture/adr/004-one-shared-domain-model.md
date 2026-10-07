# 004. One shared domain model serves streaming and storage

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Every shared business concept — an order, a customer, an event — has exactly
one canonical definition, held outside any single technology. Representations
of the concept elsewhere in the system are generated from that definition
where generation is possible and checked against it where it is not; a
representation that is neither generated nor checked is a violation of this
record, not a tolerated variant.

The same definition serves the concept in motion and at rest: the same
statement of what an order _is_ governs the records that stream between
systems and the rows that persist in storage. Changing the concept is one
change to the definition, and its consequences are visible everywhere at once.

## Context

The business system moves the same concepts across several boundaries: a
concept is entered on a screen, processed by a service, streamed between
services as a stream of events, and persisted in a database. Each of these
places speaks its own technology's dialect, and each would, left to itself,
keep its own description of the concept.

The cost of that falls due at every boundary. When two places describe the
same concept differently, someone must translate between them, and translation
code is where meaning is quietly lost: a field dropped on one side, a field
whose meaning shifted, a field added in one place and unknown in another.
These losses surface as data-integrity incidents and integration work — usually
months after the change that caused them, and usually owned by whoever is
nearest the symptom rather than whoever caused the drift.

The same concept also has to survive transport between systems that were not
built together, which means its description must be legible to receivers that
do not share the codebase that produced it.

The decision to make is where the definition of a shared business concept
lives, and how its copies across the system are kept honest.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One concept, one definition.** There is exactly one authoritative
  statement of each shared concept, and it is not owned by any one consumer.
- **R2 — Drift is detected, not discovered.** When a representation no longer
  matches the definition, a build or test fails — not a customer, later.
- **R3 — One definition in motion and at rest.** The same statement of the
  concept serves both streaming between systems and persistence in storage, so
  a record in motion and a row at rest cannot mean different things.
- **R4 — Change is one edit.** Evolving a concept is a single change to the
  definition, whose full impact is visible in one review.
- **R5 — Portable across boundaries.** The definition can be consumed by
  systems outside the codebase — partners, tools, other teams' pipelines —
  without sharing code.

## Alternatives

- **Per-stack models with mapping layers at the boundaries.** The standard
  enterprise pattern: each stack models the concept in its own terms and
  explicit translators bridge the gaps. It fails R1 — there are as many
  definitions as stacks — and fails R2 structurally: a mapping layer does not
  detect drift, it absorbs it, so divergence between two models becomes a
  runtime behaviour difference rather than a build failure. R4 then costs
  one coordinated edit per stack, per change.
- **The storage schema as the contract.** Let the database define the concept
  and derive everything else from it. It fails R2 for the parts that matter
  most: a database schema constrains the rows, not the records in motion, so
  streaming consumers evolve freely against a contract they do not consult;
  and it fails R5, binding a business concept to one storage technology.
- **Per-consumer schemas, negotiated at integration time.** Each pair of
  systems agrees a format when they integrate, with no global source. It fails
  R1 immediately — the concept is defined once per integration — and R2,
  because nothing checks that two negotiated formats still describe the same
  concept a year later.
- **Do nothing (each stack keeps its own model, no rule).** Zero cost today.
  It fails R2 by default: drift is discovered by whoever notices the data
  disagreeing, and R4 by default, since every concept change is N edits in N
  reviews by N people.

## Tradeoffs

- **Positive:** a concept change is one reviewed change with visible blast
  radius (R4); representations cannot silently disagree, because the ones that
  can be generated are generated and the rest are checked (R2); the concept
  travels outside the organisation as a plain artifact, not as a library in a
  company language (R5).
- **Negative:** the canonical definition becomes a shared dependency —
  changing it touches every consumer, so concept changes need care and a
  stated evolution policy (what may be added, what breaks consumers) that
  per-stack models never had to write down; some consumers legitimately need
  only a projection of a concept, and maintaining that projection by hand is
  exactly the kind of copy this record exists to eliminate.
- **Neutral / follow-ups:** representations that cannot be generated from the
  definition today — a hand-written model in a dynamic language, a type in the
  interface, an inline schema in a flow tool — are kept in step by convention
  until a check exists; under this record that is a gap to close, not a
  tolerated state, and the obligation is a check that fails when they drift.
  Any such representation found out of step is regenerated or generated away
  rather than reconciled by hand. Whether more representations should be
  generated is a standing question this record does not settle; for the
  interfaces between parts, the verification rule
  ([030](./030-interfaces-between-parts-are-verified-not-assumed.md)) takes
  it up — a representation nobody checks against is where drift starts.
