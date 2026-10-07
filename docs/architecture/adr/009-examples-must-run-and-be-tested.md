# 009. Every example runs and is tested, or it is removed

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Every example in the codebase is a working implementation: it runs the way the
rest of the system runs, and its behaviour is verified by tests that run in the
pipeline. An example that cannot hold that standard is removed, not annotated.

An example is not a sketch of how things are done; it is a small implementation
of how they are done, held to the same bar as anything else in the codebase.
Because the system runs everywhere it is validated
([006](./006-the-whole-system-runs-on-one-machine.md)), the examples run there
too: on an engineer's machine and in the pipeline, against real services, with
their real behaviour tested.

## Context

The codebase carries examples: small implementations that show how a part of
the system is meant to be built — a service wired to the database, a flow
wired to the stream, a screen wired to the API. People read them and copy
them, and a copied example becomes the standard for whatever is built next.
The examples are therefore how the codebase teaches, whether or not anyone
intended them to.

An example, unlike ordinary code, has no callers. Ordinary code that breaks
breaks loudly: something that depends on it fails, and the failure is
reported. An example depends on nothing, so when it stops working, nothing
notices. Its health is whoever last ran it by hand — and the first person to
discover it is broken is a reader who has already trusted it, often a new
person, who cannot tell a deliberate simplification from rot.

The two directions of error carry different costs. Removing a good example
costs a directory and the loss of a teaching artifact. Leaving a broken example
in place teaches its mistake with the authority of the codebase, and the
mistake can be copied before it is noticed.

The decision to make is what an example must do to stay in the codebase.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The claim is tested, not remembered.** The claim that an example
  works is backed by a test that runs in the pipeline; the evidence that it
  works is not that someone ran it once.
- **R2 — Breakage fails a build, not a reader.** When an example stops
  working, a build fails that day; the breakage is detected, not discovered
  later by whoever trusts the example.
- **R3 — The taught path is the shipped path.** Examples exercise the real
  mechanisms against real services, so what an example demonstrates matches
  what ships; a passing example means the path works, not that the code
  agrees with its own substitutes.
- **R4 — Examples run like the rest.** An example is brought up and run the
  way the system is brought up and run
  ([005](./005-dev-infra-starts-with-the-app.md),
  [006](./006-the-whole-system-runs-on-one-machine.md)) — no special harness,
  no machine-specific procedure.
- **R5 — Removal is cheap.** When an example can no longer hold the standard,
  removing it is a local deletion that leaves nothing dangling elsewhere.

## Alternatives

- **Keep broken examples, annotated "for illustration only".** A label marks
  the example as unmaintained and it stays for reading. It fails R1: the
  annotation is a claim no test runs, and it rots exactly like the code it
  labels; it fails R2: nothing fails when the example drifts further, so the
  label promises freshness the arrangement cannot keep. A reader copying it
  cannot tell the illustration from the rot.
- **Documentation snippets instead of implementations.** Describe the pattern
  in prose and prose only. It fails R1: a snippet in a document is never
  executed, so its correctness is a claim about the day it was written; and
  R3: the snippet is not the path, it is a quotation of the path, and the
  quotation drifts from the original in silence.
- **Examples tested against substitutes.** Keep the examples and test them
  against substitutes — stubbed services, canned responses — instead of real
  ones. It fails R3: the example then demonstrates agreement with the
  substitutes, not the path that ships, and the integration failures the
  example exists to catch are precisely what the substitutes hide.
- **Do nothing (examples live until someone complains).** Zero cost today. It
  fails R1 by default — an example's health is whoever last ran it by hand —
  and R2 by default: breakage is discovered by readers, who are the one
  audience the arrangement exists to protect.

## Tradeoffs

- **Positive:** what people copy is verified, against the real path, before
  they copy it (R1, R3); an example that rots fails a build the same day it
  rots rather than surprising a reader months later (R2); the examples double
  as the system's integration tests, so the teaching artifact and the safety
  net are the same code, maintained once.
- **Negative:** every example is a maintained implementation — code, tests,
  and the services it needs — so the honest response to an example that falls
  behind is deletion, which is cheap to do (R5) but still a loss, and the
  honest consequence is that the set of examples must stay small on purpose;
  testing against real services costs real pipeline minutes and real money
  per run, more than substitutes would
  ([012](./012-validation-runs-against-real-services.md)).
- **Neutral / follow-ups:** the full chain — producer, stream, sink, service,
  screen — is proven segment by segment, and closing that gap with a single
  test spanning all five is the test this record's own standard most wants;
  because [005](./005-dev-infra-starts-with-the-app.md) requires every
  application to have a run target, an example in an application that lacks
  one cannot yet be reached by the one-command path.
