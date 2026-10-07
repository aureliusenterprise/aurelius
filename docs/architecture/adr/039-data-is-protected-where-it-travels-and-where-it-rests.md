# 039. Data is protected where it travels and where it rests

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Data is protected in two places the system does not control by default: on
the wire between parts, and at rest in the stores it keeps. Both protections
are declared arrangements — named, configured, and checkable — not properties
assumed from the environment. Until this record is accepted, nothing in the
system encrypts either way, and that is a stated condition of the development
arrangement, not a security property of the system.

## Context

The system moves data between parts — a browser to a service, a service to a
database, a producer through the event platform into storage — and keeps data
in stores: the database, the event log, the operational signals. Today every
one of those paths and stores is unprotected: traffic between parts travels
in the clear, and data at rest sits exactly as written.

For the development arrangement this is deliberate and cheap: everything runs
on one machine, the paths never leave it, and adding certificates to every
connection would tax every run to protect a wire nobody can read. The
development record
([006](./006-the-whole-system-runs-on-one-machine.md)) is right to keep the
local arrangement simple.

The problem is what the arrangement teaches and what it ships. The examples
are the taught path: a part wired without protection in an example is wired
without protection in the next system built from it. And the system is meant
to be deployed into environments that keep business data, where both
protections are usually not optional — carried between machines someone else
operates, stored on media someone else owns. The secret-handling record
([008](./008-secrets-never-in-plaintext.md)) already decided that the
credentials themselves never exist in the clear; the data those credentials
protect has no equivalent decision.

The forces are asymmetric, and the record must hold both: protection has a
real cost per run — certificates, trust, rotation, local tooling — and its
absence has a cost that arrives all at once, in an environment where it was
assumed. The decision to make is what the system guarantees about protection,
where the guarantee may be relaxed, and how a relaxation stays visible.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The posture is stated per place.** For data in transit and data at
  rest, the record says what is protected, where protection is required, and
  where it is deliberately relaxed — a reader does not infer it from a
  localhost URL.
- **R2 — Protection is configured, not assumed.** Where protection is
  required, a mechanism enforces it and a reviewer can see the configuration;
  "the network is trusted" is not an arrangement.
- **R3 — The taught path matches the required path.** An example wired for a
  protected path shows the protected shape; where an example runs unprotected
  because it runs on one machine, the deviation is visible in the example, not
  folklore.
- **R4 — Relaxation is local and named.** The development arrangement may run
  unprotected, and says so; an unprotected path outside the development
  arrangement is a defect, not a default.
- **R5 — The check is cheap.** Whether a given path or store is protected can
  be answered from configuration, not by probing a running system.
- **R6 — New parts inherit the posture.** A new connection or store starts
  inside the declared arrangement rather than outside it.

## Alternatives

- **Protect everything, always, including local runs.** Honest and uniform.
  It fails the arrangement the whole-system record requires
  ([006](./006-the-whole-system-runs-on-one-machine.md)) in its cheapest
  form: every run pays certificate setup to protect a wire that never leaves
  the machine, and the friction teaches people to disable the protection
  everywhere it matters.
- **Protect nothing; make the deployment add it.** It fails R3 and R6: the
  taught path stays unprotected, so the deployment inherits an unprotected
  shape and discovers the gap in production; it fails R2 because the
  deployment's protection is then nobody's configuration in this system.
- **Protect only the browser-facing edge.** Familiar, since browsers insist on
  it. It fails R1: the paths inside the system — service to store, part
  through the event platform — are exactly the ones a deployed environment
  crosses machine boundaries on, and they stay declared by silence.
- **Defer entirely (the status quo).** It fails R1 by leaving the posture to
  be guessed from localhost URLs, and R3 by teaching the unprotected shape as
  the normal one.
- **Do nothing.** Costs nothing today; every requirement above is failed by
  the same silence, which is the current state described as a choice.

## Tradeoffs

- **Positive:** the development arrangement keeps its cheap local paths with
  the relaxation written down instead of implied (R4); the taught path can
  show the protected shape without dragging certificates into every run (R3);
  and a deployment gets a declared starting point — which paths must be
  protected and where the switches live (R2, R5).
- **Negative:** two postures (required, deliberately relaxed) are more to
  state and review than one absolute rule, and the line is a standing review
  question; protection has upkeep the system does not have today — trust,
  rotation, expiry — and an expired certificate fails loudly at the worst
  moment; and declaring the development arrangement unprotected is itself an
  exposure a reader may copy if R4's visibility is not kept.
- **Neutral / follow-ups:** this record is Proposed because the decision has
  not been made: no path or store is protected today and no mechanism enforces
  any posture. The credential rule it complements is already accepted
  ([008](./008-secrets-never-in-plaintext.md)) — that record protects the keys
  to the data; this one protects the data itself — and the identity of the
  parts on those paths is owned by the boundary-identity record
  ([013](./013-services-prove-who-they-are-at-every-boundary.md)), which
  decides who may speak, not whether the words are private. The placeholder
  page on data encryption under the architecture section remains a heading
  until this record is accepted and written from its answer; the operational
  signals' lifetime inside the protected stores is owned by the data-lifetime
  record ([025](./025-data-has-a-stated-lifetime.md)); and when this record is
  accepted, the named mechanisms must exist in the spine before the status
  changes.
