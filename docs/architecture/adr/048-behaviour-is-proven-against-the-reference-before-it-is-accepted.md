# 048. Behaviour is proven against the reference implementation before it is accepted

- **Status:** Proposed (the harness exists since increment 0.4; becomes Accepted when the first fixture
  recorded from the reference is replayed in CI)
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will accept a ported behaviour only when the same requests, sent to the reference
implementation and to the new system, produce equivalent responses. The reference responses are
recorded once, stored with the code and reviewed like code; equivalence ignores only the fields
that are declared volatile (generated identifiers, timestamps).

## Context

The contract the new system must honour
([046](./046-the-catalogue-keeps-its-public-contract.md)) is defined by a large existing
implementation, not by a complete written specification. Reading the old code to infer behaviour
is slow and error-prone, and reviewers cannot reasonably check a translation line by line.
Tests written by the same people who wrote the new code tend to confirm their own understanding,
including its mistakes.

## Requirements

- **R1 — An independent oracle.** Correctness is judged against something the implementers did
  not write.
- **R2 — Repeatable without the old system.** Everyday test runs do not need the reference
  implementation running.
- **R3 — Changes to expectations are visible.** When what counts as correct changes, the change
  shows up in review.
- **R4 — Intended differences are explicit.** A deliberate deviation is declared once and the
  comparison respects it, rather than being silenced test by test.

## Alternatives

- **Hand-written expected results only.** Fails R1: the expectations encode the implementer's
  reading of the old system.
- **Live side-by-side comparison on every run.** Meets R1 but fails R2: every run needs the old
  system and its storage, which is exactly what the migration removes.
- **Shadow production traffic.** Strong for R1 but fails R2 and arrives too late to guide
  increments; useful later as a release check.

## Tradeoffs

- **Positive:** reviewers see equivalence, not translation; the old system's behaviour, quirks
  included, is captured exactly; everyday runs are fast and offline.
- **Negative:** recorded fixtures go stale if the reference version changes, and someone must run
  the reference implementation to record new scenarios.
- **Neutral / follow-ups:** the scenario format, recorder and normaliser are part of the test
  tooling; results appear in the published test report
  ([049](./049-every-function-and-rule-is-traceable-to-a-test.md)). Current reference: Apache Atlas
  2.4.0 in a container.
