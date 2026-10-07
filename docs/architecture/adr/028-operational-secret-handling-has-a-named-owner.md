# 028. Operational secret handling has a named owner and a rehearsed path

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The everyday handling of real secrets — rotating one, replacing a key,
recovering a lost one, granting temporary access, removing a person — is
owned by a named role and follows a written, rehearsed path. The encryption
mechanism already in place decides how secrets are stored; this record
decides who operates it, on what rhythm, and what happens in the bad cases.
No secret, and no key, is allowed to be in a state where nobody knows who
could rotate or recover it.

The storage rule exists and is accepted elsewhere; the handling half is
explicitly recorded there as nobody's decision yet. This record is Proposed
because that decision — the owner, the cadence, the bad-case paths — has not
been made.

## Context

Secrets are encrypted to a named set of people and travel with the code as
ciphertext. Membership is already a working process: adding a person is a
reviewed change, and the re-encryption that follows is automated. That is the
easy direction — planned, reviewed, rehearsed by frequency.

The hard cases have no owner. If a credential must be rotated _today_ — a
suspected leak, a departing person with possible access, a vendor's forced
expiry — who acts, how fast, and how is the new value distributed without a
group chat? If a person loses their key, is the data recoverable, by whom,
and under whose judgement — or is the honest answer that it is not? If an
incident requires someone outside the named set to read one secret right now,
is there a path, and does anyone find out afterwards? And do the keys
themselves, and the shared secret the automation depends on, ever get
replaced, or only added to?

None of these are storage problems; the ciphertext is fine. They are
organisational problems, and the record that drew the storage line named them
as still undecided. The risk of leaving them undecided is specific: when the
bad case arrives, the path gets invented under pressure, and an invented path
around a security mechanism is how that mechanism gets bypassed for good.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — An owner exists.** One named role answers for secret handling:
  rotation, keys, membership, and the bad cases. "Who would do this?" has a
  written answer.
- **R2 — Urgent rotation is a rehearsed path.** A credential can be replaced
  and redistributed quickly, by the owner, without improvisation — and the
  path has been walked at least once before it was needed.
- **R3 — Loss has a declared answer.** What happens when a key is lost is
  written down: recovery with named custodians, or declared unrecoverable
  with the consequence owned. Silence is not a third option.
- **R4 — Temporary access is possible and visible.** A break-glass reader can
  be granted for a stated reason and period, and the grant leaves a trace the
  owner can review afterwards.
- **R5 — Removal is effective, not cosmetic.** Removing a person stops their
  future access to every secret, and the record says what it does _not_ fix —
  what that person could already have copied.
- **R6 — Keys and automation secrets are themselves rotated.** The people-keys
  and any shared secret the automation holds have a stated replacement
  cadence or a stated reason they do not.
- **R7 — Cheap enough to survive.** Routine handling stays one reviewed
  change with automated follow-through; if the path is heavier than the
  mechanism it governs, it will be bypassed, and that outcome counts as this
  record failing.

## Alternatives

- **Leave it undecided (the status quo).** The storage rule explicitly stops
  here. It fails R1 by construction, and every other requirement by
  postponement: the path will be invented during the incident that needed an
  owner. This is the current arrangement, and the reason this record exists.
- **A dedicated secrets platform with built-in rotation.** Rotation,
  short-lived credentials, access trails, and break-glass are product
  features. It answers R2, R4, and R6 well. It fails R6's cheapness test for
  a system of this size today — a second platform to operate, with its own
  custody question about _its_ root — and it does not answer R3 or R5 by
  itself; custody and offboarding remain organisational decisions wearing new
  software. A legitimate destination, not an automatic one.
- **Ad-hoc handling by senior people.** In practice this is what happens
  today: whoever built the mechanism gets paged. It fails R1 — the role is a
  person, and people leave — and R2, because an unpractised path is slower
  and less safe than a written one. It fails R4: temporary access granted
  informally leaves no trace.
- **Strictest-possible policy: no break-glass, no escrow, no exceptions.**
  Maximises the purity of the named-set rule. It fails R4 — an incident that
  cannot grant access does not stop needing the secret, it stops using the
  mechanism — and R3, because declaring data unrecoverable is only honest if
  the business has agreed to lose it.
- **Do nothing, recorded honestly.** Declaring "we accept that lost keys mean
  lost data and urgent rotation means whoever is available" is a decision an
  organisation may legitimately make at this size — but it must be written
  with R1 through R3 answered in the negative, with the risk named, rather
  than left as the current silence.

## Tradeoffs

- **Positive:** the bad cases stop being improvisations — rotation, loss, and
  break-glass have owners and paths before they are needed (R1–R4);
  offboarding means something honest, including about what removal cannot
  undo (R5);
  the storage rule finally has the operational half it deferred, so the two
  records together describe a usable mechanism rather than a vault nobody can
  open in an emergency.
- **Negative:** naming an owner makes that role a single point unless the
  path is documented well enough to hand over — the record trades silence for
  a dependency on a role; rehearsal of urgent rotation is time spent
  pretending to have an incident; and every added control (trails, cadences,
  grants) is friction that, per R7, must stay lighter than the risk it
  manages or it will be routed around.
- **Neutral / follow-ups:** the storage rule this record completes names this
  exact gap as its open end
  ([008](./008-secrets-never-in-plaintext.md)) — on acceptance, that follow-up
  is closed by this record rather than left standing; the service-to-service
  identity rules assume credentials are "issued, stored, and rotated by the
  arrangements the system runs"
  ([013](./013-services-prove-who-they-are-at-every-boundary.md)) — this
  record is where those arrangements get their owner; the cadence numbers,
  custodian counts, and grant durations belong to whoever accepts this record
  and must be named at acceptance; and the automation's own shared secret is
  currently held as a pipeline secret with no documented custodians — R6
  covers it explicitly so it cannot stay in the unexamined category.
