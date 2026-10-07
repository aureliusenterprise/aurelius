# 015. A change answers for what it caused; the state of the world is reviewed on a cadence

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The checks that block a change are exactly the checks about the change itself:
its form, its lint, its types, the tests and builds it can break, and the
absence of secrets it introduced. Findings about the state of the world —
vulnerabilities reported against dependencies, code-quality measurements,
coverage levels — are produced on every change and on a schedule, recorded
where they can be reviewed, and do not block the change that surfaced them.

The line is drawn at causation, not at severity: a person is answerable at
merge time for what their change did, and the organisation is answerable on a
cadence for the condition of everything it already ships. An advisory finding
is not ignored — it is evidence for the review that consumes it — and a
finding may be promoted to blocking when the organisation decides it will
hold changes to it.

This record settles which findings block a change; where the gate that
enforces them is defined is decided elsewhere
([014](./014-the-gate-is-defined-once-and-runs-everywhere.md)).

## Context

The organisation runs a growing set of checks: style and formatting, static
analysis, type checking, tests, builds, secret scanning, vulnerability
scanning of shipped artifacts, license review, code-quality analysis, and
coverage measurement. Each produces findings. The question each raises at
merge time is the same: does this finding stop this change?

Blocking on every finding sounds safest and behaves worst. A vulnerability in
a transitive dependency is not caused by the change under review and cannot be
fixed by its author today; blocking on it punishes unrelated work, and the
predictable response is to bypass the gate, re-run until green, or hold merges
until someone intervenes. A gate trained to be bypassed stops enforcing the
rules it was meant to keep. Coverage targets have their own failure: they are
satisfied by uninformative tests, so the number rises while the protection it
was supposed to buy does not.

Blocking on nothing is the opposite failure: findings accumulate because
nothing forces anyone to look, and the organisation cannot say whether its
shipments are getting safer or riskier.

The team is small and multi-disciplinary — the same people write the change,
see the findings, and would absorb the triage — so the arrangement must work
without a dedicated review function, and the blocking set must stay small
enough that a person can satisfy it without ceremony.

The decision to make is which findings stop a change and what the rest of the
findings are for.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The blocking set is what the change caused.** A person can satisfy
  every blocking check with their own work, in their own change, without
  waiting for anyone else's fix.
- **R2 — The everyday loop stays fast enough to keep.** The blocking set runs
  on every change without dominating the time a change takes, so nobody is
  tempted to bypass it.
- **R3 — Advisory findings are recorded, not discarded.** A finding that does
  not block still lands somewhere durable, attributable to the run that
  produced it, for whoever reviews the state of the system.
- **R4 — The state of the world is examined on a schedule.** Findings about
  dependencies and quality are produced regularly, not only when a change
  happens to touch the code that surfaces them.
- **R5 — Promotion is a decision.** Moving a finding from advisory to
  blocking is a deliberate, reviewable change, so the blocking set stays
  small on purpose.
- **R6 — Cheap to keep true.** A small team can run the whole arrangement
  without a dedicated triage role.

## Alternatives

- **Block on everything.** Every check gates every merge. It fails R1: a
  finding about a dependency, a legacy file, or a coverage number is not the
  author's to fix in their change, so merges stall on work someone else owes;
  it fails R2 as the gate grows; and it fails its own purpose, because a gate
  that blocks the unfixable trains people to bypass it.
- **Block on nothing.** Checks report and never stop. It fails R1's purpose —
  a change that introduces a secret or breaks a type reaches the shared
  history — and R3 in spirit: with no ceremony attached to any finding, the
  reports stop being read.
- **Numeric thresholds as gates: coverage floors, quality-gate scores.**
  Objective and familiar. It fails R1 — the threshold measures the state of
  the file, not the change: an unrelated legacy number blocks an unrelated
  fix — and it buys the measured property rather than the real one, since a
  coverage floor is met by tests that assert nothing. It also fails R2,
  because the cheapest local response is to lower the threshold.
- **Triage every finding before merge.** A person adjudicates each advisory
  result as part of the review. It passes R3 but fails R6: adjudication is
  standing work the small team cannot fund, and in practice it becomes a
  rubber stamp — the arrangement pays the cost of triage and keeps none of
  the attention.
- **Do nothing (checks run because they are configured, and no one consumes
  the results).** Costs nothing to keep. It fails R4 by default — scans tied
  to changes miss the world that changes nothing — and R3, because unclaimed
  reports decay into noise.

## Tradeoffs

- **Positive:** authors are stopped only by what they can fix, so the gate
  keeps its credibility and its speed (R1, R2); the serious findings still
  arrive — per change and weekly — attached to the artifacts they describe,
  so the organisation can say what it knew and when (R3, R4); the blocking
  set stays small because growing it is an explicit act (R5).
- **Negative:** known vulnerabilities sit in shipped artifacts between finding
  and fix, which is risk the organisation carries deliberately and must
  revisit on the same cadence that produces the findings; nothing numeric
  forces quality upward, so improvement depends on the review consuming the
  reports rather than on a gate enforcing it; and the promotion path from
  advisory to blocking is itself a decision the organisation has to keep
  making rather than a default it can rest on.
- **Neutral / follow-ups:** the cadence review that consumes advisory findings
  is a standing obligation of this record, and the record's premise fails if
  the reviews stop happening; naming the role that holds that review is the
  organisation's first act under this record — until it is named, the review
  is unowned and the record is only half in force; the weekly scan of the
  whole system is the arrangement's safety net for code that changes rarely,
  and its results belong to whoever the organisation names for it; the
  integrity checks that do block — signed and attested release artifacts,
  verified at publish time — gate the release rather than the change, which
  this record leaves as it is; and a secret in history is unrecoverable,
  which is why secret scanning sits on the blocking side of the line while
  vulnerability scanning does not.
