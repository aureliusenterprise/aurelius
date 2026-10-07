# 012. Validation runs against real services, not substitutes

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The behaviour of the system is validated against the real services it uses —
its database, identity provider, event platform — brought up for the run and
torn down after it. Substitutes — stubbed services, canned responses,
hand-written fakes — are not the default path for validating how the system
behaves.

A test that passes against a substitute is evidence about the substitute.
Only a test that passes against the real thing is evidence about the system,
and the organisation acts on the second kind.

## Context

The system is assembled from parts that talk to services: a service reads and
writes storage, consumers move records through a stream, a front end calls an
API that delegates admission to an identity provider. The failures that cost
the business money live in those conversations — a driver behaves differently
than the client assumed, a constraint the code never expected, an
authentication handshake that only the real service enforces.

Validation can exercise those conversations against the real service or
against a stand-in. A stand-in is cheaper per run and faster to start, and it
carries a hidden cost: it is a second implementation of the service's
behaviour, written by people who only know the behaviour the code already
assumes. Where the assumption is wrong, the stand-in agrees with it — the
substitute hides precisely the failures the test exists to catch, and does so
silently, forever. The stand-in is also code, and a second codebase with its
own bugs and its own upkeep is exactly the cost a small team cannot fund
twice.

The decision to make is what the system's behaviour is validated against, and
what a passing test is allowed to be evidence of.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — A passing test is evidence about the shipped path.** The services a
  test exercises are the services production uses, at the same interface, so
  the test's claim transfers to what ships.
- **R2 — Fidelity does not decay in silence.** The arrangement contains no
  hand-written model of a service's behaviour that can quietly disagree with
  the service, because nothing checks the model.
- **R3 — Runs need no accounts or network.** The services a test uses are
  brought up by the run itself on the machine doing the validating, so an
  unattended run and an offline machine reach the same result.
- **R4 — The cost stays bounded.** Real services cost real minutes and real
  money per run; the arrangement keeps that cost small enough that validation
  still happens on every change rather than being rationed.
- **R5 — Cheap to keep true.** Adding a validated part, or changing what it
  depends on, is a local edit by the person making the change, not work
  spread across a maintained fake world.

## Alternatives

- **Substitutes everywhere: stubs and fakes per service.** Fast, cheap,
  hermetic. It fails R2 structurally: a substitute is written from the same
  assumptions as the code it stands in for, so the two agree by construction
  and disagree with the service in exactly the places nobody noticed. It
  fails R1 for the same reason — the test's claim ends at the substitute's
  boundary — and it fails R5, because the substitute world is a second
  codebase that must track every service it imitates.
- **Recorded traffic replayed as the service.** Capture real conversations
  and replay them in tests. It passes R1 on the day of capture and fails R2
  afterwards: the recording is a claim about one day, the real service
  evolves, and the replay agrees with the old behaviour in silence. It also
  fails R4 in practice — recordings rot and must be re-captured, which is the
  upkeep of the substitute option with extra steps.
- **Real services hosted by the platform.** Use the live services rather than
  local copies. It passes R1 outright but fails R3: every run needs accounts,
  network, and a shared mutable service, so unattended runs wait on access
  someone provisioned and two runs contaminate each other.
- **Do nothing (each test picks its own level).** Zero cost today. It fails
  R1 by default: a green suite becomes a mix of claims about the system and
  claims about substitutes, and no reader can tell which is which — so the
  suite's green stops meaning anything in particular.

## Tradeoffs

- **Positive:** a passing test is evidence about the shipped path (R1), so
  confidence transfers to production without a gap to reason about; there is
  no fake world to build or maintain, which removes a whole category of
  silent disagreement (R2, R5); runs are self-contained, so the pipeline and
  an offline machine see the same result (R3).
- **Negative:** every run pays real startup cost and real resource cost, so
  validation must stay targeted — the parts a change can reach — or the cost
  will ration the testing; some services have no local equivalent at all, and
  those runs wait on the exception rather than the rule.
- **Neutral / follow-ups:** a dependency that exists only as a hosted service
  is validated against a local equivalent, and drift between the two is
  treated as a defect, not environment noise; each such dependency needs a
  named validation arrangement, and until it has one it is a hole in R1 that
  the organisation is carrying knowingly.
