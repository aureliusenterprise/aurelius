# 044. Every change carries two human signatures

- **Status:** Accepted
- **Date:** 2026-10-08
- **Deciders:** Aurelius Enterprise

## Decision

Every change that merges into the mainline carries two human signatures: the
**task owner** — the person who asked for the change, who can explain it, and
who states how far they verified it locally — and **one reviewer**, a
second person who confirms independent understanding. An automated assistant
may produce, test, and review a change, but it signs nothing: accountability
is carried by the team and cannot be offloaded to a tool. The rule is enforced
by a mechanism that refuses the merge, not by custom: a change without the
second approval cannot merge.

## Context

The repository is changed routinely by automated agents as well as by people,
and the cost of producing a plausible diff has fallen sharply. The obligation
attached to a change has not: the team must be able to own what it ships, and
ownership requires understanding.

Before fast generation, the author's understanding was largely a side effect
of writing the code by hand. Now a change can arrive working, gated, and
reviewed by machines while nobody on the team fully understands it. The
failure is quiet: it surfaces at the next incident, the next change to the
same area, the next handover — with a delay, which is what makes it debt
rather than a defect.

The organisation already requires a second pair of eyes: the contributor
guide has always stated that every pull request is reviewed by at least one
other team member. That rule was written for a slower generator; what changes
when code is produced quickly is how load-bearing it becomes, and a rule held
only by custom is the first thing a fast queue erodes.

The decision to make is what a change must carry before it merges, and who is
answerable when the author is a tool.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — A human answers for every change.** For every merged change there is
  a named person who can explain it and who carries it; a tool cannot be that
  person, and "the assistant wrote it" is not an answer to "who owns this?".
- **R2 — Understanding is independent.** At least one person besides the task
  owner reads the change for understanding before it merges; self-approval is
  not approval.
- **R3 — Verification is stated, not assumed.** The task owner records how
  far they verified the change locally, so a reviewer knows whether "it works"
  means lint passed or the real system ran; the pipeline's full gate is the
  guarantee, and the statement is the owner's honest report of what they have
  personally seen.
- **R4 — The rule has an enforcement point.** The second signature is required
  by a mechanism that refuses the merge, not by a convention that erodes when
  delivery is late.
- **R5 — Cheap enough to keep.** Two signatures on a small team's typical
  change is minutes, not a ceremony; the rule must not push people to route
  around it.
- **R6 — Knowledge moves with review.** The reviewer is chosen at least partly
  for who should learn the area, so review doubles as knowledge spread rather
  than rubber-stamping.

## Alternatives

- **One signature (the status quo).** The task owner merges whatever passes
  the gate. It fails R2: the gate checks the change's form and behavior, not
  whether anyone understands it, and R6 — knowledge concentrates in whoever
  prompted the change.
- **Machine review is enough.** Let automated review and the gate stand in for
  the second human. It fails R1 and R2: a machine verdict is evidence, not
  accountability, and the organisation still needs a person who can explain
  the change six months from now.
- **Committee approval for agent-authored changes.** Treat agent changes as
  riskier and require more sign-offs. It fails R5 and contradicts the
  no-privileged-path rule ([022](./022-the-codebase-explains-itself-to-its-agents.md)):
  risk follows the change's blast radius, not the identity of the typist, and
  a special lane trains the team to avoid declaring assistant involvement.
- **Custom only.** Hold the rule by convention, with nothing refusing the
  merge. It fails R4: the first urgent merge that skips review establishes the
  exception, and at generated volume the exceptions become the rule silently.
- **Do nothing.** Costs nothing today; it fails R1 the first time a change
  breaks and nobody on the team can explain it.

## Tradeoffs

- **Positive:** every merged change has a human who can explain it (R1) and a
  second human who is starting to (R2, R6); the verification statement makes
  the strength of "it works" visible at review time (R3); the merge mechanism
  turns the oldest review rule in the guide into an enforcement point (R4),
  which is what
  [017](./017-shared-concepts-change-only-compatibly.md) asks of
  review-only conventions.
- **Negative:** two humans per change is the scarcest budget in a small team,
  and generation volume can make the second signature the bottleneck — the
  pressure will be to approve quickly, which R6 mitigates only if reviewer
  selection stays deliberate; declaring the task owner adds one line of
  ceremony to every pull request; and the merge mechanism can be overridden by
  repository administrators, so it needs the same habit as the gate.
- **Neutral / follow-ups:** the mechanism that makes R4 true lives in the
  hosting platform's merge settings — an implementation detail of where the
  rule is enforced, not part of the decision itself. The pull request template
  carries the two signatures and the verification statement. Review by an
  assistant is
  governed separately
  ([043](./043-ai-assisted-review-informs-the-signatures-it-does-not-replace-them.md));
  the no-privileged-path rule is this record's neighbour, not its source
  ([022](./022-the-codebase-explains-itself-to-its-agents.md)); what the
  reviewer may rely on the gate for is decided by the blocking rule
  ([015](./015-a-change-answers-for-what-it-caused.md)).
