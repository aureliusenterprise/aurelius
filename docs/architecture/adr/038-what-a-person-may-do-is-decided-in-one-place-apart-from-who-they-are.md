# 038. What a person may do is decided in one place, apart from who they are

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The answer to "what is this person allowed to do?" is held and enforced in one
named place, deliberately apart from the answer to "who is this person?".
Surfaces ask that place and act on the answer; they do not invent their own
rules in code. Until this record is accepted, every authenticated person can
do everything on every surface, and that is a stated condition, not a
security property.

## Context

The system already knows who a person is: one identity provider admits people
and every surface verifies what it issues, so no surface keeps its own
account list. That answers admission. It does not answer permission. Today,
once a person is admitted anywhere, they are admitted everywhere: the screens,
the APIs behind them, and the operational tooling act on the verified identity
and nothing else.

For the system as it stands — an arrangement being validated, with examples
that demonstrate the shape — that is workable, and pretending otherwise would
be false. But the system is meant to be deployed into environments that keep
business data, and there the question "why could this person change that?"
has to have an answer. Without a decided arrangement, the answer arrives by
accident: the first feature that needs a restriction grows a private check,
the second feature grows a different one, and permission — the one security
property auditors ask about most directly — becomes folklore scattered through
surface code.

The forces are the same ones that settled identity: several surfaces, one
truth, and revocation that must take effect everywhere at once. Permission
inherits those forces and adds one: a permission rule that lives inside a
surface can only be changed by releasing that surface, while the business
reason for the rule changes on its own schedule.

The decision to make is where the answer to "what may this person do?" lives,
who enforces it, and what a surface must do to honour it. It is deliberately
separate from the identity decision: a system can change how it authenticates
without rewriting its permissions, and vice versa.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One answer about permission.** Exactly one authoritative statement of
  what each person or role may do; no surface keeps a private rule that
  overrides or supplements it.
- **R2 — Revocation of permission is one action.** Withdrawing an allowance
  withdraws it at every surface without releasing those surfaces.
- **R3 — Surfaces ask, then act.** A surface enforces by consulting the
  decided answer, not by embedding the rule itself; the security-critical
  judgement is written, reviewed, and patched once.
- **R4 — The answer is auditable.** "Who could do X, and when?" can be
  answered from the arrangement's own records rather than reconstructed from
  surface code and logs.
- **R5 — Permission runs where validation runs.** The permission path is live
  on one machine and in the pipeline, so the restricted path is exercised
  routinely, not discovered in a production incident.
- **R6 — Cheap to keep true.** A new surface or a new action joins the decided
  arrangement rather than inventing its own; the default is the shared answer,
  not a private check.

## Alternatives

- **Permission inside each surface.** Each part decides for itself what an
  authenticated person may do. It fails R1 — the truth is wherever the last
  check was written — R2, because withdrawal is a release per surface, and
  R4, because the audit is a code survey.
- **Permission at the network edge only.** One gate in front of everything
  decides. It fails R3 for anything the edge cannot see — an event consumed
  directly, a call between parts — and R4, because the edge knows what was
  attempted, not what the business action meant.
- **Role names baked into surface code.** Familiar and quick. It fails R2 and
  R3: the meaning of a role is then distributed across every release, and
  changing what a role may do is a code change everywhere at once.
- **Defer permission entirely (the status quo).** Honest for a system with no
  business data yet. It fails R1 by leaving the question unowned, and it
  fails R6 by making the first urgent restriction a bespoke check under time
  pressure — the arrangement every later one copies.
- **Do nothing and hope the deployment adds it.** It fails R5: a permission
  path that exists only in a deployment is a path no earlier run has
  exercised.

## Tradeoffs

- **Positive:** permission questions have one address (R1, R4); withdrawal is
  one act instead of a release checklist (R2); surfaces stay thin, as identity
  made them thin; and the restricted path is exercised where every other
  security path is exercised (R5).
- **Negative:** one more decision point in the request path, with its own
  failure mode to design for — what a surface does when the permission answer
  is unreachable is a question this record must eventually answer; the
  arrangement is one more part to run locally and in the pipeline; and naming
  roles is a business act that will be wrong sometimes, so the arrangement
  must make being wrong cheap to fix.
- **Neutral / follow-ups:** this record is Proposed because the decision has
  not been made: today every authenticated person can do everything, and no
  mechanism enforces otherwise. The identity arrangement it sits beside is
  already accepted
  ([007](./007-one-shared-identity-provider.md)) and this record deliberately
  does not re-open it — admission and permission stay separate answers even if
  one product ends up holding both. The placeholder page on access management
  under the architecture section remains a heading until this record is
  accepted and written from its answer; the machine-identity question for
  part-to-part calls is owned by the boundary-identity record
  ([013](./013-services-prove-who-they-are-at-every-boundary.md)) and is not
  this record's to decide; and when this record is accepted, the named
  mechanism must exist in the spine before the status changes.
