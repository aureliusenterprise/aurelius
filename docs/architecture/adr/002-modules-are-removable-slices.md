# 002. Modules are removable as whole slices

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Every module in the repository belongs to exactly one of two categories: it is
part of the spine — the core that always stays, in every copy of this system —
or it belongs to an optional capability that can be removed as a whole slice.

A capability owns its applications, libraries, and development infrastructure
together, and deleting it — code, wiring, configuration, and documentation in
one pass — leaves the remainder working. Partial removal is not a supported
state: a team either takes a capability in full or does not take it at all.

## Context

The repository holds a complete business system: an interface, backend
services, a streaming data pipeline, shared libraries, and the development
infrastructure that runs them. One multi-disciplinary team builds all of it
today, and no capability is currently being removed.

The system is also meant to be read and reused as a whole, which is the reason
it lives in one repository (see [001](./001-single-monorepo.md)). Work taken
from it is expected to take a subset: a form-driven service has no use for a
streaming pipeline, and a team running workloads on serverless infrastructure
has different infrastructure needs than one running long-lived services. That
creates a tension: the more capabilities the system demonstrates, the more
useful it is as a reference, and the more a person has to sift through to find
the part relevant to them.

Without a rule about how the system may be taken apart, two failure modes are
open. Someone who wants to drop a capability has to discover, by trial and
error, which libraries, build wiring, configuration keys, and documents belong
to it — and will usually leave some behind. A capability added with no rule
has no reason to stay separable, so it threads a dependency through the middle
of something general-purpose. Either way the repository accumulates parts that
belong to no one, and the cost of understanding it rises for everyone who
reads it.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Complete removal by deletion.** A capability can be removed by
  deleting the directories that belong to it, without digging through the
  rest of the repository to find hidden wiring.
- **R2 — The remainder still works.** After removal, what remains builds,
  tests, and runs without reference to anything deleted.
- **R3 — Wiring is not interleaved.** A capability's build wiring,
  configuration, and documentation are not interleaved with those of the rest
  of the system, so removal is not an editing task on files someone else owns.
- **R4 — Cheap to take back.** Adding a capability later does not require
  reworking what is already there.
- **R5 — Cheap to keep true.** The rule holds with a small team maintaining it,
  without a dedicated owner per capability.

## Alternatives

- **Free-form composition: any module may depend on any other.** Maximum
  flexibility, and the default state of a repository nobody disciplines. It
  fails R1 and R2: there is no boundary at which a capability ends, so removal
  becomes a hunt through shared build files and configuration, and the remover
  cannot tell what is safe to delete. It fails R3 outright: the wiring of one
  capability runs through files the whole system shares.
- **Fine-grained modules, one per reusable component.** Precise dependency
  graphs and maximal reuse. It fails R5: keeping a large graph of small modules
  coherent — their wiring, versions, and documentation — is ongoing work a
  small team cannot fund. It also degrades R1, because "which parts form the
  streaming capability?" stops having a single answer.
- **Fork per capability combination.** Each team takes the subset it needs and
  maintains a fork. It appears to satisfy R1, but fails R2 in the direction
  that matters: the fork diverges, so fixes stop flowing between it and the
  original, and R4 fails because taking an improvement back from the original
  is a rework of everything the fork already changed.
- **Do nothing (document nothing about removal).** Zero cost today. It fails
  R1 and R2 by default: the first team to drop a capability discovers the
  boundaries by breaking the build, and writes down nothing for the next one.

## Tradeoffs

- **Positive:** a capability can be taken or dropped as a unit, so the system
  serves teams that need only part of it (R1, R2); ownership is legible,
  because everything belonging to a capability sits together (R3); the rule
  costs little to honour, since it asks for colocated wiring rather than new
  machinery (R5).
- **Negative:** capabilities cannot share infrastructure freely — where two of
  them rely on the same backing service, one of them has to own it, and
  removing that owner leaves the other with a service and no reason for it;
  some general-purpose work is duplicated rather than shared, because sharing
  it would cut a capability in half; every addition has to be classified as
  core or optional, a judgement call that occasionally needs re-litigating.
- **Neutral / follow-ups:** nothing in the build enforces these boundaries, so
  the rule holds only because the repository makes each capability's parts easy
  to see — which depends on every project documenting itself
  ([003](./003-every-project-documents-itself.md)). Two obligations follow from
  the rule itself rather than from any particular state of the repository, and
  both are carried by the documentation rule rather than by new machinery:
  infrastructure shared by more than one capability is owned by the capability
  whose directory holds it, and that ownership is stated in the capability's
  own documentation, where a remover will read it; and a part belongs to its
  capability by sitting in the capability's directories and being listed in
  the capability's documentation — a part that is neither is invisible to a
  removal sweep, which is a defect in that documentation, not bad luck.
