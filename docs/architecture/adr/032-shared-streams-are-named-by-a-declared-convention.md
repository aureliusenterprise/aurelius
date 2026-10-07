# 032. Shared streams are named by a declared convention

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The name of a stream that carries business events is chosen by a stated
convention rather than by whoever creates it: the name says what the stream
carries and which version of it, and it deliberately says nothing about which
environment the stream lives in. A reader who can see a name can tell what
flows through it and whether it is the current version, without asking.

The convention exists and is followed by the business streams it was written
for; it has simply never been recorded as a decision, only written in
guidance. This record promotes the convention to a decision so that it
survives the guidance being rewritten, and so a name that ignores it is
visibly a deviation rather than a second opinion. The few names that already
ignore it are named as follow-ups rather than hidden.

## Context

Streams are the seams between the system's parts, and unlike code, a stream
name is not local to the change that creates it. A name is referenced by
producers, consumers, connectors, configuration, dashboards, and operational
runbooks, in several languages and the habits of whoever writes the next
consumer, and it is very expensive to change once anything is attached to it. A stream created today
with a name that describes its author's branch, or its environment, becomes a
permanent artifact nobody can rename.

The organisation already chose a convention, and the business streams follow
it: lowercase, component-separated names that read as _what category, what
thing, which version_, with a length limit, and with an explicit decision not
to encode the environment. That last choice is the load-bearing one: encoding
an environment in a name means the same logical stream has different names in
different places, which makes every producer and consumer configuration
environment-specific and turns a portable system into a pile of per-place
wiring. Keeping the environment out of the name is what lets the same
definition travel.

None of this is written down as a decision. It lives in a guidance page,
which means a future rewrite of that page can quietly reverse it, and a new
stream can be named by instinct — including the environment-encoding the
convention rejects — with nothing to point at. The question this record
answers is what a stream name is allowed to say, and why.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The name is self-describing.** From the name alone, a reader can
  tell what the stream carries.
- **R2 — Version is part of identity.** An incompatible change to what a
  stream carries produces a new name, so old and new can coexist without
  guessing.
- **R3 — Environment is not part of identity.** The same logical stream has
  the same name everywhere it runs, so definitions travel between
  environments unchanged.
- **R4 — The convention is uniform.** Every stream follows one shape, so a
  reader never has to learn a second naming style to read a list of streams.
- **R5 — The convention is stated where names are made.** Whoever creates a
  stream meets the rule at that moment, not in a review comment later.
- **R6 — Cheap to keep true.** Naming a new stream correctly is the default,
  not an extra step.

## Alternatives

- **Free naming.** Fastest for whoever creates a stream, and the state without
  a convention. It fails R1, R2, and R4 immediately: a list of streams stops
  being readable, and incompatible shapes either collide under one name or
  hide under names that do not say they replaced anything.
- **Environment encoded in the name.** Familiar, and tempting because it
  makes a running environment legible at a glance. It fails R3 directly: the
  same stream gains a different name per environment, so every producer,
  consumer, and connector needs environment-specific configuration — which
  contradicts the arrangement that settings, not names, are what differ
  between environments
  ([018](./018-settings-arrive-at-startup-through-one-channel.md)).
- **Central registry of stream names.** A person or tool approves each name.
  It passes R4 by force and fails R6: naming a stream becomes a request, and
  requests during delivery get bypassed, which leaves the registry incomplete
  and the convention optional.
- **Convention by example only (the status quo).** Guidance describes the
  shape and existing streams demonstrate it. It passes R1 and R2 in practice
  and fails R5 — guidance is read after the name is chosen, if at all — and
  leaves the whole convention one documentation rewrite away from being
  silently abandoned, which is the reason for this record.
- **Do nothing.** Costs nothing and keeps the convention unwritten; it fails
  R5 by construction and R3 the first time someone encodes an environment
  because nothing said not to.

## Tradeoffs

- **Positive:** a stream list is readable without a guide (R1, R4); an
  incompatible change gets a name that says so, which is what lets old and
  new readers coexist (R2); stream definitions are portable because the
  environment is not baked into them (R3); and the convention now has a
  record to be cited by, rather than a page that can be rewritten around.
- **Negative:** names are longer and more formal than anyone's instinct, and
  the length limit occasionally forces an abbreviation that costs the
  self-describing property it exists to protect; a version suffix invites
  streams to be versioned reflexively rather than when a change genuinely
  breaks readers; and the convention is enforced by review rather than by a
  check, so a non-conforming name can still land — a named gap of this record
  rather than a tolerated state.
- **Neutral / follow-ups:** what makes a change incompatible enough to
  deserve a new version is decided by the compatibility rule
  ([017](./017-shared-concepts-change-only-compatibly.md)), and this record
  only supplies the name that change travels under; the guarantees carried
  _inside_ a stream — duplication, ordering, undeliverable events — belong to
  [027](./027-every-stream-carries-a-stated-delivery-guarantee.md), and the
  convention for dead-letter names follows the same shape as the stream it
  parks for; and a check that refuses a non-conforming name at creation is
  the enforcement point this record does not yet have, and should acquire.
  Six names in the repository already ignore the convention: three
  throwaway topics that end-to-end tests create, which read as one
  kebab-case phrase rather than the component shape, and three internal
  topics a connector names for itself, which also exceed the length limit.
  Whether the convention covers such throwaway and infrastructure topics —
  or whether they are explicitly out of scope — is not yet written down,
  and should be.
