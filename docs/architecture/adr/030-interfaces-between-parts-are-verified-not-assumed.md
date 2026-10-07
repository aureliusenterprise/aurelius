# 030. Interfaces between parts are verified, not assumed

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Where one part of the system offers an interface another part consumes, the
agreement between them is stated once and checked, so a change that breaks a
consumer is caught where it is made rather than where it is felt. A consumer
does not rely on remembering what the provider sends; the check remembers for
it.

The domain concepts behind these interfaces already have one canonical
definition
([004](./004-one-shared-domain-model.md)); this record covers the interfaces
themselves — the callable surface a consumer actually depends on — which is
today restored by hand on each side with nothing comparing them. It is
Proposed because the checking mechanism does not exist and the direction has
not been chosen.

## Context

The system's parts talk to each other over interfaces: the screens people use
call the services, services call each other, and the shapes that cross those
boundaries are the business concepts. An interface is a promise in both
directions — the provider promises what it will return, the consumer promises
what it will send — and a promise that only one side has written down is a
promise nobody enforces.

Right now each side writes its own version of the agreement. The provider
declares what it serves; the consumer re-declares, by hand, what it believes
the provider serves. Nothing compares the two. The provider does publish a
machine-readable description of its interface, and a test confirms that the
description exists — but nothing downstream reads it, so the description can
say one thing while the consumer assumes another, and both are green.

This is the same failure the shared domain model was written to prevent, one
layer out. That record decided there is one canonical definition of a concept
and made the copies accountable to it
([004](./004-one-shared-domain-model.md)), while explicitly leaving open
whether more representations should be generated rather than hand-kept. The
interface is the next representation, and it is currently the least checked:
a concept can be canonical and still be transported wrongly, because the
transport agreement is folklore on both sides.

The cost lands predictably. A provider changes a field's name, its type, or
whether it can be absent; every consumer that assumed the old shape keeps
compiling and starts failing at runtime, in a screen a person is looking at,
far from the change that caused it. The larger the number of consumers, the
more copies drift, and the more each change is a coordination exercise
instead of a check.

One fact makes fixing this cheaper here than it would be elsewhere: every
consumer lives in the same repository as the provider it reads
([001](./001-single-monorepo.md)), so finding them is a search, not a
campaign. The arrangement that makes interface verification expensive in a
distributed estate is absent, which is why this record's requirements are
worth meeting at the cheapest possible point — before the estate grows.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The agreement is stated once.** One place says what the interface
  is; provider and consumer both answer to it rather than to each other's
  guess.
- **R2 — Drift fails the change that caused it.** A change that makes an
  implementation disagree with the stated agreement is stopped by a check at
  commit or review time, not discovered in use.
- **R3 — Consumers are found, not remembered.** When the agreement changes,
  the parts that depend on it are identifiable mechanically, so "did we get
  everyone?" has an answer that does not depend on attention.
- **R4 — The agreement is readable by whoever integrates.** A person or a
  machine connecting to an interface can learn what it accepts and returns
  without reading the provider's source or asking anyone.
- **R5 — Compatible change stays cheap.** Adding an optional element to an
  interface costs the same small step as adding one to a concept, not a
  regeneration ceremony across every consumer.
- **R6 — The check is honest about what it covers.** Where a check cannot
  compare the two sides, that gap is named, so nobody mistakes an unchecked
  interface for a checked one.

## Alternatives

- **Hand-mirrored interfaces (the status quo).** Each side writes what it
  believes. It fails R1 by construction and R2 completely — nothing compares
  the two statements, so drift is invisible until runtime. It also fails R3:
  finding consumers means searching for copies of a shape and hoping the
  search was clever enough.
- **Generate consumers from the provider's description.** The provider's
  statement becomes the only statement, and consumers are produced from it.
  It satisfies R1, R3, R4, and R5 elegantly. It fails R2 on its own —
  generation proves the consumer matches the description, not that the
  provider honours it — and it fails R6 unless the description is treated as
  a contract with teeth rather than documentation with a syntax. It also
  assumes every consumer can tolerate a generated shape, which a user-facing
  interface often cannot.
- **Contract tests between the two sides.** Each consumer states what it
  expects; a test runs the expectation against the real provider. It answers
  R2 and R6 directly and survives a provider that cannot or will not publish
  a description. It fails R1 as usually practised — expectations live in
  consumer tests, so the agreement is still written N times — and R4, because
  a test suite is not a document an integrator can read.
- **Coordination by review.** A convention plus a careful reviewer who knows
  both sides. It fails R2 and R3 exactly as often as reviewers are new,
  tired, or far from the other stack — which, in a system that deliberately
  spans several languages on one machine
  ([006](./006-the-whole-system-runs-on-one-machine.md)), is often. It is the
  current arrangement with a title.
- **Do nothing.** Costs nothing and keeps every interface change a runtime
  discovery; it fails R1 through R4 by leaving the agreement unwritten and
  unchecked, which is the state described as an option.

## Tradeoffs

- **Positive:** interface breakage moves from user screens to the change that
  caused it (R2); consumers of a change are enumerable rather than remembered
  (R3); integrators get a readable statement instead of an archaeology
  project (R4); the shared-concept decision finally covers how concepts
  travel, not only what they are.
- **Negative:** the agreement becomes an artifact someone must maintain, and
  a stale agreement is worse than none because it is trusted; generation
  trades hand-written consumer code for generated code that must be lived
  with, and user-facing shapes resist being generated; and enforcement
  requires a checking point that does not exist yet, so until it does the
  record leans on review — counted here as a gap to close, not a tolerated
  state.
- **Neutral / follow-ups:** the machine-readable description the provider
  already publishes, and the test that only confirms it exists, are the
  obvious seed for the check — turning that test into a comparison is the
  cheapest first act on acceptance; the standing question that the shared
  model record leaves open, about which representations should be generated
  rather than hand-kept
  ([004](./004-one-shared-domain-model.md)), is answered by this record for
  interfaces and only for interfaces; how an interface changes without
  breaking readers is governed by the compatibility rule
  ([017](./017-shared-concepts-change-only-compatibly.md)) and this record
  adds no new rule about direction, only about verification; and the streams
  side of "how concepts travel" — ordering and duplication — is owned by
  [027](./027-every-stream-carries-a-stated-delivery-guarantee.md).
