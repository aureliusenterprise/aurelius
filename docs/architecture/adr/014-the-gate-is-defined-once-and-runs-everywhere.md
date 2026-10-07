# 014. The gate that refuses a change is defined once

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The checks that gate a change — formatting, linting, typing, secret scanning,
and the basic well-formedness of every file in the repository — are defined in
exactly one runnable place, and the pipeline runs that same definition rather
than a second list written for it.

A rule therefore cannot exist in one moment and not the other: what refuses a
change when it is committed is what refuses it in the pipeline, and adding a
rule is a single edit that takes effect at both moments. Checks too expensive
for the everyday moment — full test suites, builds — run in the pipeline and
are named as pipeline-only rather than quietly absent from the local gate.

This record settles where the gate is written and how often it runs; which
findings it blocks is decided elsewhere
([015](./015-a-change-answers-for-what-it-caused.md)).

## Context

Every change the organisation ships passes through two moments of validation:
the moment a person commits it, and the moment the pipeline reviews it before
merge. Both moments need to know the rules; the question is how many times the
rules are written down.

Two separate lists — a local script and a pipeline definition — start
identical and end apart, because whoever adds a rule usually thinks of one of
the two places. The cost of that drift falls on the person whose change passes
the first moment and fails the second: the repair is a round trip through a
pipeline run, and the lesson learned is that local passes mean nothing. A gate
that is discovered late also trains people to treat the pipeline as the
adversary rather than as evidence.

The team is small and multi-disciplinary, so the people maintaining the rules
are the people subject to them; a rule kept in two places is a rule they will
maintain twice, which is how rules come to be inconsistent and then
distrusted. The repository spans several stacks, so a gate defined per stack
would mean several lists with several gaps, and the gap would be where the
next defect lands.

The decision to make is how many times the gate is written down, and which
moment learns the rules first.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One definition of the gate.** The rule set exists once, as an
  artifact that can be run; there is no second list kept in step by memory.
- **R2 — No rule discovered only in the pipeline.** A change that passes the
  local gate passes the pipeline's gate, except for checks explicitly named
  as too expensive for the everyday moment and for findings that only the
  pipeline's whole-repository scope can produce.
- **R3 — Cheap to keep true.** Adding, changing, or removing a rule is one
  edit by the person who wants it, effective at both moments, not a two-place
  change that can half-land.
- **R4 — The gate is reviewable.** The rule set is versioned, so a change to
  what is enforced is visible and reviewable as a change in itself.
- **R5 — Every stack is inside the gate.** The same definition covers every
  technology in the repository, so no stack is silently ungated.

## Alternatives

- **The pipeline as the only gate.** Define the rules once, but run them only
  in the pipeline. It passes R1 and R4 but fails R2 by construction: every
  rule is discovered at its most expensive moment, after review time has been
  spent, and the repair loop is a commit and a pipeline run rather than a
  local fix. It also fails the everyday purpose of a gate — keeping bad form
  out of history — because it lets it in and complains afterwards.
- **Two hand-maintained lists.** A local script and a pipeline definition,
  written separately. It fails R1 outright and R3 with it: the lists are
  maintained by whoever remembers both, which over time is no one, and the
  drift between them is invisible until a change is caught in it.
- **A gate per stack, wired into each project.** Each technology enforces its
  own rules in its own way. It fails R5 — the gate becomes the union of what
  each stack happened to adopt, and a new stack starts ungated — and R3,
  because a rule added "everywhere" is N edits in N places.
- **Do nothing (rules live in review comments).** The cheapest arrangement
  to start with. It fails
  R1 by default — the rules exist in whoever reviews pull requests — and R4,
  because enforcement is a person's mood rather than a reviewed artifact;
  consistency then scales with the reviewer's stamina.

## Tradeoffs

- **Positive:** a person who can commit can merge — the pipeline adds no
  surprises of form (R2); a rule is one edit that lands everywhere at once
  (R1, R3); the rule set is a reviewed artifact, so relaxing or tightening
  enforcement is visible history (R4); every stack enters the same gate
  (R5).
- **Negative:** the local gate must run wherever people work, so its tooling
  has to be available on every machine — a dependency on the versioned
  development environment ([011](./011-the-development-environment-is-a-versioned-artifact.md))
  rather than on whatever a machine happens to have; and the gate must stay
  fast enough to run before every commit, or people start bypassing it, which
  makes gate runtime itself a constraint to defend.
- **Neutral / follow-ups:** the checks named as pipeline-only are a standing
  exception this record requires to stay named — a check that becomes cheap
  enough for the everyday moment belongs in the local gate, and a check that
  becomes too slow belongs in the pipeline, either way as a reviewed change
  to the definition; the local gate runs against the files a change touches
  while the pipeline runs it against the whole repository, so a change to a
  shared rule — a lint configuration, a shared type — can pass locally and
  fail in the pipeline: a second named exception to R2 rather than a hidden
  one. Whoever edits a shared rule file runs the gate across the whole
  repository before pushing; everyone else keeps the everyday moment fast.
