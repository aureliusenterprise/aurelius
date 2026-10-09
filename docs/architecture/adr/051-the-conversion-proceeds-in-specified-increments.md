# 051. The conversion proceeds in increments, each defined by a written specification

- **Status:** Accepted
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will convert the catalogue in increments. Each increment is one change of reviewable size that
ports one named behaviour; it begins with a short written specification of the behaviour — scope,
rules with identifiers, origin in the old system, deviations, acceptance — and it is not complete
until its rules are tested, its parity checks pass, and its decisions are recorded.

## Context

A full rewrite delivered at once cannot be reviewed, and a review that cannot be done becomes a
signature without understanding ([044](./044-every-change-carries-two-human-signatures.md)).
The old system is large; its behaviour is spread over many classes. Without a stated scope per
change, reviewers cannot tell an omission from a decision, and the project cannot tell how far it
has come.

## Requirements

- **R1 — Reviewable size.** A reviewer can understand one change in one sitting.
- **R2 — Stated meaning.** What a change is supposed to do is written down before it is judged.
- **R3 — Measurable progress.** At any moment it is clear which behaviours are done.
- **R4 — Decisions travel with the change.** The reasons for a change are recorded in the same
  change, not reconstructed later.

## Alternatives

- **Big-bang rewrite, reviewed at the end.** Fails R1 and R3.
- **Increments without written specifications.** Meets R1 but fails R2: the code becomes its own
  specification and review checks consistency, not intent.
- **Feature tickets in an external tracker.** Partly meets R3 but fails R4: the reasoning lives
  outside the repository and is lost with the tracker.

## Tradeoffs

- **Positive:** every change has a stated purpose and an objective definition of done; progress is
  visible in the repository itself.
- **Negative:** writing a specification takes time before any code exists, and splitting large
  behaviours into increments occasionally needs temporary scaffolding.
- **Neutral / follow-ups:** the roadmap, specification template and design log live in
  [the conversion ledger](../conversion/index.md); the pull request template asks for the
  increment and the records it touches.
