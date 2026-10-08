# 043. AI-assisted review informs the two signatures; it does not replace them

- **Status:** Accepted
- **Date:** 2026-10-08
- **Deciders:** Aurelius Enterprise

## Decision

Automated review — an assistant reading the diff and leaving findings — is a
permitted and welcome first pass on any change, human- or agent-authored. Its
findings are treated by the same rule as every other finding: those about the
change itself block when the gate enforces them, and those about the state of
the world are advisory evidence for the cadence review
([015](./015-a-change-answers-for-what-it-caused.md)). An automated review
comment is never an approval: the two human signatures stand
([044](./044-every-change-carries-two-human-signatures.md)), and dismissing a
machine finding is a human act, recorded as one.

## Context

Review is the scarcest capacity in a small team, and fast generation multiplies
the volume of diff arriving at it. The team already uses assistants to read
diffs — the commit history carries the residue of applied review feedback —
but the practice has no stated boundary, and an unstated practice drifts in
the direction of least effort: first toward treating a machine's approval as
the second signature, then toward dismissing its findings without reading
them, then toward skipping the human review the machine seemed to make
unnecessary.

Each drift has a known failure. A machine cannot be accountable for a merged
change ([044](./044-every-change-carries-two-human-signatures.md)), so an
approval that is not a human's leaves R1 unanswered. Machine findings include
plausible mistakes, and a finding dismissed unread is a defect adopted with
confidence. Conversely, treating every machine finding as blocking would
import the world's noise into the merge gate — the exact failure the blocking
rule was written to prevent
([015](./015-a-change-answers-for-what-it-caused.md)) — and would train the
team to bypass the review as they bypass a noisy gate.

The decision to make is what automated review is allowed to count as, and what
it can never count as.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The signatures stay human.** Automated review may inform both
  signatures but cannot satisfy either; no workflow accepts a bot approval as
  the second pair of eyes.
- **R2 — Machine findings follow the blocking rule.** A finding blocks a
  change only when the defined gate enforces it; the reviewer's judgement of
  a machine comment never changes what blocks.
- **R3 — Dismissal is a human act.** Every rejected machine finding is
  dismissed by a named person, so a wrong machine verdict cannot silently
  become a merged defect, and the dismissal is visible in the review.
- **R4 — Volume does not lower the bar.** The practice must hold when review
  volume is high; if it only works when the queue is short, it will be the
  first thing skipped under pressure.
- **R5 — Cheap to keep true.** No new roles, queues, or dashboards; the
  practice rides on the review surface the team already uses.

## Alternatives

- **No automated review.** Keep review purely human. It passes R1 trivially
  and fails the reason the practice exists: at generated volume, human review
  without a machine first pass becomes the bottleneck that squeezes
  understanding out of the second signature.
- **Machine approval counts as the second signature.** It fails R1 outright:
  a bot cannot explain the change in six months, cannot carry it in an
  incident, and cannot be the accountable party
  ([042](./042-every-dataset-has-an-owner-who-answers-for-it.md) makes the
  same point about ownership).
- **Machine findings always block.** It fails R2 and R4: machine review
  produces confident nonsense at a steady rate, and a gate that must be
  argued with is a gate that gets bypassed — the failure mode named in
  [015](./015-a-change-answers-for-what-it-caused.md).
- **Machine findings are invisible (advisory-only, off the review).** Findings
  go to a side channel instead of the pull request. It fails R3 and R5:
  dismissals happen off the record, and a second surface is a second thing to
  maintain and then ignore.
- **Do nothing (status quo, unstated).** The practice continues without a
  boundary; it fails R1 by drift — each relaxation is individually reasonable
  and together they replace the second signature.

## Tradeoffs

- **Positive:** the team keeps the capacity gain of a machine first pass
  without letting it redefine accountability (R1); machine findings arrive
  where humans already read, at no new ceremony (R5); and the dismissal rule
  turns each wrong machine verdict into visible evidence about the tool
  rather than an invisible defect (R3).
- **Negative:** machine review still consumes human attention to triage its
  findings, and at high false-positive rates that tax can exceed the saving —
  the response is to tune or drop the reviewer, never to relax R3; and the
  rule depends on reviewers actually reading machine comments, which is the
  same review-discipline dependency the instruction layer carries
  ([022](./022-the-codebase-explains-itself-to-its-agents.md)).
- **Neutral / follow-ups:** the boundary's R1 rests on the two-signature rule
  and the merge mechanism that enforces it
  ([044](./044-every-change-carries-two-human-signatures.md)); R3's dismissal
  habit rests on review discipline, the same dependency the instruction layer
  carries ([022](./022-the-codebase-explains-itself-to-its-agents.md));
  whether machine findings should ever be promoted to
  blocking is a decision under
  [015](./015-a-change-answers-for-what-it-caused.md), not this record.
