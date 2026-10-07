# 034. Signals meet at one replaceable collection point

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every part exports the same three signals — traces, metrics, and logs — to
one collection point that is part of the system, over a standard protocol,
and never to a storage or visualisation backend directly. The collection
point is the single seam: the tools that store and display the picture live
behind it and can be changed without touching the parts.

This decision was already in force before it was written down: the
observability stack the development arrangement starts
([006](./006-the-whole-system-runs-on-one-machine.md)) includes a collection
point that every instrumented part exports to, and the storage and
visualisation backends behind it are known to the parts only through it.
Where the picture is allowed to live — inside the system, never with a
vendor — is a separate decision
([016](./016-the-system-observes-itself-internally.md)); this record covers
the shape of the seam the signals pass through.

## Context

The running picture is assembled from what every part emits, and the
organisation has to decide how the emissions reach the tools. The two failure
shapes are known: parts that point directly at their storage backends, so
changing a backend means touching every part, and parts that each speak a
different tool's protocol, so the picture cannot be assembled at all. Both
are the absence of a seam.

[016](./016-the-system-observes-itself-internally.md) decides that the
picture is produced and consumed inside the system. That decision is
compatible with several internal shapes — every part wired to its own
storage, one shared collector, a sidecar per part — and the shape is a real
decision with its own consequences: it determines what it costs to change an
observation tool, and what it costs to instrument a new part. Separating the
two records keeps each checkable on its own: a system can keep its data
inside the boundary and still have no seam, and the gap should be visible as
exactly that.

A standard protocol at the seam is what makes the arrangement portable: it is
also the condition under which a future production arrangement could export
elsewhere without re-instrumenting the parts — a step
[016](./016-the-system-observes-itself-internally.md) does not allow without
a new record, but the seam is what keeps that door from being welded shut.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One seam.** Parts hand their signals to a single collection point;
  no part knows the address of a storage or visualisation backend.
- **R2 — A standard protocol.** The handover uses a protocol the wider
  ecosystem speaks, so neither the parts nor the backends behind the seam are
  tied to this organisation's tooling choices.
- **R3 — The observer is replaceable.** Storage and visualisation tools
  behind the collection point can be changed, upgraded, or swapped without
  touching any part.
- **R4 — Instrumenting a part is cheap.** A new part points at the collection
  point and exports; it gains the whole picture rather than one backend's
  slice of it.

## Alternatives

- **Each part exports to whichever backend it needs.** No collection point;
  parts point at their own storage. It fails R1 — the backends become N
  dependencies instead of one seam — and R3 with it: changing a backend is a
  change to every part. It can satisfy
  [016](./016-the-system-observes-itself-internally.md) perfectly — all data
  stays inside — which is exactly why it needs its own record to rule out.
- **A collection point speaking an in-house protocol.** A seam exists, but
  the protocol is this organisation's own. It fails R2: every backend behind
  the seam must be written or adapted for it, so the observer is not
  replaceable in practice (R3), and a new part needs custom wiring (R4).
- **A sidecar or agent per part instead of one collection point.** Each part
  hands its signals to something beside it. It keeps R2 and R4 but strains
  R1 — the picture is assembled from N agents whose configuration must agree
  — and adds a per-part mechanism to operate where one shared point suffices.
- **Point parts at the backends today, add the seam later.** Cheapest at the
  start. It fails R3 at the moment of decision — the first backend change
  touches every part — and defers R1 into a migration whose cost grows with
  every part added before it.
- **Do nothing (leave the seam implicit in the stack).** The state this
  record corrects. It fails no requirement of the mechanism itself and fails
  the organisation's: the next person to add a part or a backend would not
  know the seam exists, and wiring around it would not fail any check.

## Tradeoffs

- **Positive:** changing an observation tool is a change behind the seam, not
  a change to the parts (R3); a new part is instrumented once and gains every
  backend's view (R4); and the standard protocol keeps the door open to a
  future production arrangement without re-instrumentation, without
  committing to one.
- **Negative:** the collection point is one more running part to start, keep
  healthy, and reason about when signals go missing — a failure at the seam
  blinds every backend at once; and the seam's standard protocol is the
  lowest common denominator, so a backend's richer features are reachable
  only behind it, never through the parts.
- **Neutral / follow-ups:** the browser-rendered part currently sends its
  signals to an address fixed in its own build rather than to the collection
  point its deployment names
  ([018](./018-settings-arrive-at-startup-through-one-channel.md)) — a
  deviation from this record's single seam until the address arrives through
  that channel, and worth checking per deployment once it does; how the
  collection point itself is deployed in a customer's environment follows
  [016](./016-the-system-observes-itself-internally.md)'s boundary rule, and
  a deployment that names no collection point runs blind by choice, which is
  a gap to name rather than tolerate; and how long the signals the collection
  point holds are kept is a lifetime question owned by
  [025](./025-data-has-a-stated-lifetime.md), not by this record.
