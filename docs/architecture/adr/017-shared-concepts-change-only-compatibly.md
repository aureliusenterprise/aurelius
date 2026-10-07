# 017. Shared concepts change only in ways that keep readers working

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

A change to a shared business concept is allowed only in the directions the
compatibility rule permits: a change must leave every existing reader of the
concept working without being changed first. Additive change — a new optional
element — is the default direction; a change that would break an existing
reader is a new version of the concept, carried alongside the old one for a
stated period, never an edit to what readers already consume.

The rule is checked where it can be checked — a change that violates it must
be refused rather than warned about — and where it cannot yet be checked, the
change carries the same obligation by review. This record settles the
direction concepts may move in; where the canonical definition lives and how
copies are kept honest is already decided elsewhere
([004](./004-one-shared-domain-model.md)).

## Context

The business concepts — an order, a customer, an event — are consumed the
moment they are defined: records carrying them sit in streams waiting to be
read, rows persist for years, and receivers outside the organisation parse
them on their own schedule. A concept therefore has consumers the organisation
does not control and cannot pause: data already in motion, data already
stored, and partners already integrated.

That is what makes concept change different from ordinary code change. Code
and its callers are updated together in one change; a concept's older readers
cannot be updated before the change lands, because they are running elsewhere
or the data they read was written earlier. A concept edited in a breaking
direction does not fail at the edit — it fails later, at whichever reader
cannot parse what arrived, usually far from the change that caused it.

The organisation has chosen one canonical definition for each concept
([004](./004-one-shared-domain-model.md)); that decision made every consumer
depend on one statement, which is the point — but it also means the statement
now needs a rule for how it may change, because a single definition edited
freely concentrates exactly the breakage it was meant to prevent. The
guidance written so far recommends a compatibility strategy without naming
who enforces it or what happens when a change genuinely must break, so the
rule lives nowhere and every concept change re-decides it.

The decision to make is which changes to a shared concept are permitted, and
what a change that cannot be permitted becomes instead.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Existing readers keep working.** After a concept changes, every
  reader built against the earlier version still reads what arrives, without
  being changed or redeployed first.
- **R2 — Old data stays readable.** Records written before the change remain
  parseable afterwards, for as long as they exist in streams or storage.
- **R3 — Breakage is a new version, not an edit.** When the business genuinely
  needs a change readers cannot absorb, the old version continues to be served
  while the new one is adopted, with a stated path and period for the
  transition.
- **R4 — The rule is enforced, not advised.** A change that violates the rule
  is stopped by a check, not left to whoever remembers the guidance.
- **R5 — The rule is stated where consumers can read it.** A team integrating
  with the concept can learn what may change and what is stable without asking
  anyone.
- **R6 — Cheap to keep true.** Honouring the rule costs a concept change a
  small, routine step, not a ceremony.

## Alternatives

- **Free change: edit the concept whenever the business needs it.** Fastest
  for the person making the change, and the default without a rule. It fails
  R1 and R2 by construction: readers built against the old shape meet data
  they cannot parse, and stored records become unreadable — the failure lands
  at the worst time, far from its cause. It fails R5 as well, since nothing
  tells a consumer when the ground moved.
- **Freeze the concept: no breaking changes ever, in any form.** Protects
  readers absolutely. It fails R3's purpose: businesses do need changes
  readers cannot absorb — a removed field, a retyped identifier — and a rule
  with no exit for them is quietly abandoned the first time one is genuinely
  needed, taking the rest of the rule with it.
- **Warn but don't stop: advisory checks and review discipline.** Familiar and
  low-friction. It fails R4: a warning that merges anyway is the same
  arrangement as no rule, differing only in logs; and R5, because "ask the
  elders" is not a stated rule.
- **Version everything up front: every concept change creates a new version.**
  It passes R1 and R2 but fails R6 — additive changes, which are the routine
  majority, would each spawn a parallel version to maintain and reconcile —
  and it degrades R5, because consumers face a version matrix where one
  evolving concept would serve.
- **Do nothing (keep recommending a strategy in guidance).** This is where
  the repository stands, so it costs nothing. It fails R4 by default — the
  recommendation has no enforcement point — and R3, because there is no
  stated path for the breaking change that guidance cannot prevent.

## Tradeoffs

- **Positive:** concept changes stop being an incident risk — readers built
  earlier keep working, so streams and stored data survive the change (R1,
  R2); the rare breaking need has a named route instead of an exception made
  under pressure (R3); consumers can integrate against a stated contract
  rather than an observed habit (R5).
- **Negative:** the everyday direction of change is widened rather than
  deepened — reshaping a concept becomes a versioned migration, which is
  slower than an edit and honestly sometimes feels like bureaucracy; running
  two versions side by side is real cost that must end on a stated date or
  become permanent; and enforcement requires a checking mechanism the
  organisation does not fully have yet, so until it exists the rule leans on
  review, which this record counts as a gap to close, not a tolerated state.
- **Neutral / follow-ups:** the compatibility level at which the registry
  refuses changes is the enforcement point of this record and must be set
  deliberately rather than inherited from a default — until it is set, R4 is
  aspirational at that boundary and treated as such; representations of a
  concept that are hand-kept rather than generated are checked against this
  rule by review until a check exists, the obligation
  [004](./004-one-shared-domain-model.md) already carries; storage sinks that
  are configured not to follow concept changes are deliberate, and keeping a
  table and a concept in step is then a named migration task rather than an
  accident; and the stated period for running an old version alongside a new
  one belongs to the concept's owner to name at the time of the break, not
  later. Records written later lean on this rule without restating it:
  [027](./027-every-stream-carries-a-stated-delivery-guarantee.md) covers how
  a stream behaves while this record governs what its events contain,
  [030](./030-interfaces-between-parts-are-verified-not-assumed.md) verifies
  interfaces against this rule rather than re-deriving it, and
  [032](./032-shared-streams-are-named-by-a-declared-convention.md) supplies
  the name a breaking change travels under; if this record is ever
  superseded, those three are the dependent set to re-check.
