# 001. Keep one monorepo for every stack

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

We will keep all first-party work — every language, application, library, and
piece of development infrastructure — in a single repository, orchestrated by
one task runner that understands each toolchain natively.

A change that crosses a technology boundary must remain possible as a single
reviewable, atomic commit. Modules may be removed wholesale, but the
organisation will not split what remains into separate repositories.

## Context

The organisation delivers a business system that spans several technology
stacks: a user-facing application, backend services, a streaming data
pipeline, shared libraries, and the infrastructure that runs them together.
The capabilities only pay off end to end — a shared business concept, such as
a customer or an order, is realised from the screen through the services and
into storage.

The business situation:

- Work is delivered by one multi-disciplinary team, so a single feature
  routinely touches several technologies at the same time, and the same
  people move between the interface, the services, and the pipeline.
- The team is small: everyone shares responsibility for the shared libraries,
  the delivery workflow, and the documentation, and no one owns a single
  technology.
- As the team grows, new developers need to understand how the pieces fit
  together rather than bootstrap their own setup.
- Release cycles follow business milestones, not individual technologies, so
  a change to a shared concept is expected to land everywhere at once.

The decision to make is how many sources of truth the delivery path has —
one place where the code and its workflow live, or several — and what binds
them together. The cost of getting it wrong is paid for years afterwards —
in every review that spans a boundary, in every release that needs
coordination, in every new joiner's ramp-up — and it is paid by the people
making those changes, not by whoever made the layout decision.

## Requirements

Any acceptable layout must deliver:

- **R1 — Atomic cross-stack change.** A change to a shared concept (for
  example a domain model) can be reviewed and shipped as one unit, without
  coordinating releases across separately versioned deliverables.
- **R2 — One way to run the system.** There is a single, documented way to
  build, test, and run the whole thing, so onboarding and CI learn one entry
  point rather than one per toolchain.
- **R3 — Coherence at small-team cost.** The small team can keep the shared
  code, workflow, and documentation consistent as they evolve.
- **R4 — One place to learn the system.** A new developer can browse the
  whole system in one place and see how the pieces fit together.
- **R5 — Ownership matches staffing.** Ownership boundaries reflect the team
  that exists — one multi-disciplinary group — not boundaries the organisation
  would have to staff.

## Alternatives

- **Separate repository per technology or per stack (polyrepo).** The common
  enterprise default; it gives each stack an independent release cycle and
  access boundary. It fails R1: a shared-concept change becomes a
  multi-repository, multi-release coordination effort with windows where the
  parts disagree. It also strains R3 — workflow and documentation upkeep is
  duplicated per repository — and R4, since a new developer inherits a set of
  repositories and the wiring between them rather than one place to learn the
  system.
- **A collection of folders with no unifying task runner.** Keeps each
  ecosystem pure and is cheapest to set up. It fails R2: there is no single
  way to build, test, or run anything, so "run the whole system" — the
  everyday question for a new developer or a CI pipeline — has no answer, and
  R3 suffers because every toolchain's workflow must be re-invented and
  re-maintained separately.
- **Do nothing (each technology keeps its own repository).** Zero decision
  cost today. It fails R1 and R3 by default: shared code and documentation
  drift apart between the parts, and a new developer receives pieces rather
  than a working whole.

## Tradeoffs

- **Positive:** cross-stack changes are atomic and reviewed once (R1); the
  workflow is defined once and applies everywhere (R2, R3); a new developer
  can follow one business concept end to end without leaving the repository
  (R4).
- **Negative:** the repository must carry tooling for several ecosystems at
  once, and every toolchain decision has to coexist with the others; checkout
  and CI cost grows with everything included; there is no repository-level
  access boundary, so module discipline is a convention, not a wall.
- **Neutral / follow-ups:** because the wall is not enforced by repository
  boundaries, rules that keep the monorepo from rotting — modules removable as
  whole slices ([002](./002-modules-are-removable-slices.md)), documentation
  colocated with what it documents
  ([003](./003-every-project-documents-itself.md)) — become the compensating
  mechanisms and need their own records.
