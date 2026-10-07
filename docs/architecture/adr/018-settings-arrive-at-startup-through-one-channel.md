# 018. Settings arrive at startup through one channel and fail loudly

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every setting a running part needs — addresses, ports, feature switches,
credentials it reads rather than owns — arrives through the environment the
part starts in, and is read and validated once, at startup. A part that starts
has therefore been told everything it needs and found it usable; a missing or
malformed setting stops the start rather than surfacing at first use.

Nothing environment-specific is compiled into a part. The same unit that was
validated is reconfigured for each environment by changing what it is told at
startup, never by rebuilding it — which is what makes the deployment rule in
[010](./010-the-unit-validated-is-the-unit-that-ships.md) possible at all.
The channel is defined by who supplies the settings — the environment the
part is deployed into — not by the mechanism that delivers them: a part
rendered in a browser cannot read a server's environment, so its deployment
places the settings beside it for pickup at run start, which is the same
channel one step removed. Where a setting is a secret, this record governs
how it arrives, not where it rests: that is decided elsewhere
([008](./008-secrets-never-in-plaintext.md)).

## Context

The system's parts are configured by different forces: an engineer changes a
port to avoid a collision, the pipeline points a part at a throwaway service,
a deployment points the same part at the real one. The settings themselves
belong to the part; the values belong to the environment. Every stack in the
repository has its own historical habit for how a value reaches code — a
compiled-in file per environment here, a settings document there, a value read
deep inside a request path somewhere else — and each habit carries the same
two costs.

The first cost is the rebuild trap. A setting fixed at build time means a new
environment is a new build, which quietly breaks the rule that the unit
validated is the unit deployed: the deployment then carries a build no
validation ever saw. The second cost is late failure. A setting read when
first used fails at an ordinary-looking moment, far from the start-up that
omitted it, and a part that starts broken and fails at first use is worse to
operate than one that refuses to start: the second is obvious, the first is a
support ticket.

The team is small and multi-disciplinary and moves between stacks, so a
different configuration habit per stack is a different habit to remember per
stack — and the person debugging a misconfigured part at two in the afternoon
does not care which ecosystem the part was written in.

The decision to make is how a setting reaches a running part, and when a wrong
setting is allowed to reveal itself.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One channel for every stack.** A setting reaches a running part the
  same way regardless of which technology the part is written in, so one
  mental model covers the system.
- **R2 — Reconfiguring never rebuilds.** Pointing a part at a new environment
  changes only what it is told at startup; the unit itself is untouched, so
  the validated unit is still the deployed unit.
- **R3 — Bad settings fail at startup.** A missing or malformed setting stops
  the part from starting, with a message naming the setting — not a failure at
  first use.
- **R4 — The running configuration is knowable.** What a running part was
  told can be enumerated from the outside, so a misconfiguration is a fact
  that can be checked rather than a hypothesis.
- **R5 — Configuration and secrets stay distinct.** Ordinary settings are safe
  to carry as committed dev defaults; a value that is not safe to publish
  follows the secrets arrangement rather than this one.
- **R6 — Cheap to keep true.** Adding a setting is a local edit to the part
  and its environment description by the person adding it.

## Alternatives

- **Compile settings into the part per environment.** The traditional
  per-environment build: a config file chosen at build time. It fails R2
  outright — every environment becomes its own build — and with it the
  confidence transfer [010](./010-the-unit-validated-is-the-unit-that-ships.md)
  exists to protect; it fails R1 in spirit too, because the environment's
  values now live in the build system rather than with the environment.
- **A central configuration service.** One service answers "what should this
  part be told?", live. It passes R1 and R4 elegantly but fails the
  arrangement the system runs under: every start would wait on a service and
  a network ([006](./006-the-whole-system-runs-on-one-machine.md)), so the
  offline machine and the unattended run need a fallback — and that fallback
  is a local file, which means the organisation now has two channels and has
  decided nothing.
- **Settings files beside the code, read at will.** Each part keeps its own
  config document and reads what it needs when it needs it. It fails R2 —
  the file travels inside the unit, so environment values ship inside the
  artifact — and R3, because a value read at first use fails at first use;
  it fails R1 as well, since the mechanism is whatever each stack's library
  happens to offer.
- **Framework defaults with silent fallbacks.** The part runs on built-in
  defaults unless told otherwise. It fails R3 by design: a missing setting is
  indistinguishable from an intentional default, so a part pointed at the
  wrong place by omission looks healthy until it writes somewhere wrong.
- **Do nothing (each stack keeps its habit).** This is the current state and
  costs nothing to keep. It fails R1
  by default — every stack answers the same question
  differently — and R3 unevenly, because some habits fail loudly and some do
  not, which is worse than all failing loudly.

## Tradeoffs

- **Positive:** one question — "what was this part told at startup?" — answers
  configuration for every stack (R1, R4); environments differ by values, never
  by builds, so the deployment rule holds (R2); a misconfigured part is loud
  at start instead of quiet at first use (R3); adding a setting is local work
  (R6).
- **Negative:** the environment description becomes part of every run path, so
  a typo in an environment file is now a startup failure the organisation has
  to tolerate being the commonest incident — the correct trade, but the
  incidents are real; startup validation must be written deliberately for each
  part, because a part that merely reads strings discovers its problems late;
  and a browser-rendered part cannot read a server's environment, so its
  settings are fetched at run start from where its deployment placed them,
  which is the same channel one step removed and needs the same
  startup-validation habit to be worth anything.
- **Neutral / follow-ups:** the deviations are named rather than tolerated:
  the Node-RED example bakes its production settings document into its unit
  — an environment value inside the artifact — and reads its settings through
  the host framework rather than validating them at startup; the
  browser-rendered example fetches its settings at run start but does not
  validate them, so a missing or malformed document surfaces at first use —
  the failure R3 forbids. All deviate until their settings arrive at startup
  and are checked. The line between an ordinary setting and a secret is
  enforced by the check
  [008](./008-secrets-never-in-plaintext.md) already owes; and the enumerated
  startup configuration is where a future operational review will look first,
  which makes the startup message's quality a standing obligation rather than
  a nicety.
