# 020. Dependencies stay current by default; majors move by decision

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Third-party dependencies are kept current by default: every ecosystem the
system consumes — packages, containers, workflow actions, tooling — is
monitored on a schedule, and routine updates arrive as reviewable changes
automatically, one dependency at a time. The same gate that refuses
hand-written changes refuses them ([014](./014-the-gate-is-defined-once-and-runs-everywhere.md)),
so an update is accepted by evidence, not by trust.

Breaking changes are the exception, and are handled deliberately. Where an
update crosses a major boundary for a dependency whose upgrade is a project
rather than a bump — the frameworks the system is built on — automation
proposes nothing and the upgrade happens as planned work, on a date the team
chooses. Everything else, including majors of ordinary libraries, flows
through the automatic channel and is judged by the gate.

The default is currency: a dependency is old only because someone chose to
keep it that way, and the choice is visible.

## Context

The system stands on a large base of third-party code: language packages in
three ecosystems, container images for every backing service, CI actions, and
the toolchain itself. None of it is frozen; all of it changes underneath the
system whether the system acts or not. The question this record answers is
who decides when the base moves, and how quickly.

Two failure modes bracket the options. Let updates accumulate and the system
ages into a position where every dependency is several generations behind and
each catch-up is a breaking change compounded with the next — the upgrade that
was avoidable weekly becomes unavoidable and expensive yearly, and security
fixes arrive only as part of those expensive jumps. Chase every update the
moment it publishes, on the other hand, and the team spends its attention on
churn: most updates fix nothing the system cares about, and some carry real
regressions that deserve a human deciding whether the affected part is worth
the risk this week.

The arrangement that resolves the bracket is to separate the two kinds of
movement by their cost, not by their version number. An update that the gate
can judge — build it, test it, and see — is cheap to accept and cheap to
revert, so it should arrive automatically and often: small, single-purpose,
reviewable changes, exactly like ordinary commits. An update the gate cannot
judge — where the tests pass but the upgrade is a migration of how the system
is written — is not a bump at all, and automating it produces a stream of
changes nobody can meaningfully review. The frameworks the system is built on
are the case in point: their majors are deliberate, batched decisions, so
automation is pointed away from them and toward everything else, where its
judgement (the gate's) is actually the right instrument.

This record is the input side of the delivery rule
([019](./019-the-system-releases-as-one-versioned-whole.md)): a released
version is a consistent snapshot only if the base under it is known and
recent, and lockstep release is what makes an accepted update actually reach
users rather than sitting unreleased.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — No ecosystem left unwatched.** Every kind of third-party thing the
  system consumes is monitored; "we forgot to watch the containers" is not a
  failure mode the arrangement permits.
- **R2 — Routine updates need no human initiative.** A person does not
  remember to check for updates; they arrive as proposed changes on a
  cadence, small enough that each is one dependency's movement.
- **R3 — Updates are judged like changes.** A proposed update passes the same
  gate as a hand-written commit; an update that breaks the system is refused
  by evidence rather than discovered after merge.
- **R4 — Framework majors are planned, not automatic.** Upgrading what the
  system is built on is scheduled work with a decision in front of it, not a
  bot's pull request merged under time pressure.
- **R5 — Age is visible.** A dependency that is deliberately held back is
  recorded as held back, with the hold a choice someone made rather than
  drift; a dependency nobody thought about is distinguishable from one
  someone pinned on purpose.
- **R6 — Security fixes are not gated by cadence.** A fix for a known
  vulnerability reaches the system through the same automatic channel at
  least the same speed as everything else — the default posture is what makes
  this automatic rather than heroic.

## Alternatives

- **Update by hand, when someone remembers.** The pre-automation default. It
  fails R2 and R6 outright — the update arrives when a person happens to care,
  which correlates with novelty, not need — and R1, since watching eight
  ecosystems by hand is a job nobody holds. It is the arrangement this record
  exists to replace.
- **Update everything automatically, majors included.** Maximum currency,
  minimum ceremony. It fails R4: a major of a foundational framework is a
  migration dressed as a bump, and merging it on gate-green evidence alone
  ships a decision nobody made — the gate proves the old code still runs, not
  that the new idiom was adopted deliberately. It also fails R5 in reverse,
  because a system that never holds anything back has no record of what it
  depends on being stable.
- **Pin everything, upgrade on a fixed schedule (quarterly review).** A
  stability-first posture. It passes R4 and R5 comfortably but fails R6 — a
  vulnerability fix waits for the review — and fails R3's spirit: batched
  upgrades arrive as large multi-dependency changes the gate can judge only
  as a bundle, so a failure names ten suspects instead of one.
- **Update only what has a known vulnerability (security-only automation).**
  The minimal posture. It fails the premise: by the time a vulnerability is
  published and scanned, the system has been running the flaw for however
  long the version was old, and the fix lands as the same kind of jump this
  record exists to avoid. It fails R2 and R6 — currency by exception is
  currency by heroics.
- **Do nothing (no update automation at all).** Zero setup cost. It fails R1,
  R2, R5 and R6 by definition, and quietly fails R3 as well: un-updated
  dependencies eventually demand a large change, which is the least reviewable
  kind.

## Tradeoffs

- **Positive:** the base under the system is known-recent at every release
  (supports [019](./019-the-system-releases-as-one-versioned-whole.md));
  updates arrive one-at-a-time so a failure names one suspect (R3); security
  fixes ride the default channel rather than an emergency one (R6); watching
  is automated across every ecosystem, so coverage is a configuration fact,
  not a habit (R1).
- **Negative:** review volume is a real cost — most proposed updates fix
  nothing the system cares about, and the team must build the reflex of
  merging gate-green single-dependency changes quickly, or the queue rots and
  the posture decays into the batched-upgrade failure mode it replaced; the
  line between "ordinary library" and "framework the system is built on" is a
  judgement that must be maintained as the system grows, and a wrong call
  either spams the team with migration PRs or silently automates one; and
  held-back dependencies need their holds recorded, which is a small
  discipline with no immediate payoff.
- **Neutral / follow-ups:** the automation configuration's ignore list is
  the registry of holds, and each entry carries the reason for its hold, so a
  deliberate pin is distinguishable from an oversight (R5) — keeping those
  reasons current as holds change is the standing discipline, and the list is
  where a future operational review should look first, because a held
  dependency is a known liability with a shelf life; watching covers the
  manifests each ecosystem names, but not every pin: the tool versions a hook
  file lists beside its own hooks are a dependency surface the current
  monitoring does not watch, and R1 is unmet there until it does; a security
  fix rides the ordinary queue, and a queue that rots stalls it like anything
  else — the cadence review that consumes the vulnerability reports is where
  a stalled security fix must be escalated, because no blocking check will
  ([015](./015-a-change-answers-for-what-it-caused.md) keeps those findings
  advisory), and without that link R6 is only as fast as the queue; if the
  gate ever grows a security-scanning stage that can fail a change
  ([014](./014-the-gate-is-defined-once-and-runs-everywhere.md) leaves that
  open), this record's R6 is its main justification; and the cadence itself
  (weekly proposals) is an operational parameter, not part of the decision —
  the decision is that the default is currency and the exception is
  deliberate; and this record covers the libraries inside a runtime, not the
  runtime itself — the support window for a language or runtime version, and
  who decides its major bumps, is owned by
  [031](./031-runtime-versions-have-a-declared-support-window.md), which
  names the seam between the two records as still unowned for runtime minor
  releases.
