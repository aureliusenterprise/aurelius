# 008. Real secrets are encrypted; only dev defaults are committed

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Real secrets never exist in the codebase as plaintext. A secret the system
needs is encrypted to a named set of recipients and committed as ciphertext;
what the codebase carries in plaintext is dev defaults — values safe to publish.
The set of people who can read the secrets is exactly the recipient list, and
changing that set is an edit to the list.

Reading and writing secrets is part of running the system, not a visit to a
service beside it: bring-up decrypts what a run needs
([005](./005-dev-infra-starts-with-the-app.md)) and the loop never waits on a
secret store ([006](./006-the-whole-system-runs-on-one-machine.md)). The
ciphertext travels with the code, so the codebase can be cloned, forked, and
cached without any of it becoming a breach.

## Context

The system runs on secrets: database passwords, service tokens, signing keys.
They must reach every place the system runs — an engineer's machine, the
pipeline, production — and between the moment a secret is created and the
moment a running service uses it, the secret rests somewhere. Where it rests,
and who can read it there, is the decision.

The codebase's history is permanent and endlessly copied. A committed file
reaches everyone who ever clones the repository, every pipeline cache, every
fork, and cannot be recalled from any of them. A real secret committed in
plaintext is therefore not a mistake to be corrected but a breach to be
remediated: every credential it contained must be rotated, and the exposure
must be audited for as long as the history existed.

The people who need to read the system's secrets are a small, named set — the
people who build and operate it. That makes the question "who can read this
secret?" answerable explicitly, by encrypting to named recipients, rather than
answered implicitly by whoever happens to hold a copy of the code.

The decision to make is where real secrets rest between creation and use, and
who can read them there.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — History never carries plaintext.** A real secret that enters the
  codebase exists there only as ciphertext; plaintext is never the default
  path for a real value.
- **R2 — The loop never waits on a secret service.** A developer reaches a
  fully running system on their own machine, without a live secret store to
  reach. The system is meant to be runnable without accounts or network; the
  arrangement for secrets must not reintroduce that dependency through a side
  door.
- **R3 — Access is a list, not a trail.** Who can read the secrets is one
  explicit set; removing a person from it ends their future access by editing
  the set, not by hunting copies.
- **R4 — One mechanism everywhere.** The same mechanism serves an engineer's
  machine, the pipeline, and deployment, so no environment invents its own
  handling of the same secrets.
- **R5 — Cheap to keep true.** Adding a secret, or adding a person, is a small
  edit to project files, not a standing project of its own.

## Alternatives

- **A cloud secret manager, nothing in the repository.** Keep every secret in
  the platform's secret service and fetch at runtime. It fails R2: the
  everyday loop — and every unattended run — would reach a service behind a
  cloud account, so the system stops being runnable offline
  ([006](./006-the-whole-system-runs-on-one-machine.md)); and it fails R4,
  because the local loop then needs a fallback the platform never uses, and
  that fallback is a plaintext file.
- **A vault per environment.** Operate a dedicated secret store for each
  environment. It fails R2 for the same reason, R4 — the everyday loop now
  starts and configures a vault — and R5: standing up, versioning, and
  administering vaults is a standing project, not a small edit.
- **Trust the ignore list.** Keep plaintext files and rely on the ignore list
  to keep them out of history. It fails R1: an ignore list is a wish, not a
  wall — one forced add, one renamed file, one tool that commits what it was
  given, and the breach is permanent; it fails R3 as well, because the answer
  to "who can read this" becomes "everyone who ever held a copy".
- **Do nothing (secrets are handled as they come up).** Zero cost today. It
  fails R1 by default — every password pasted into config or chat is a future
  remediation — and R3 by default, because access is whatever the copies say
  it is.

## Tradeoffs

- **Positive:** the codebase can be cloned, forked, mirrored, and cached
  without any of those acts becoming a breach (R1); development stays fully
  offline-capable (R2); who can read secrets is one list, and revoking a
  person is an edit to it (R3); one mechanism serves machine, pipeline, and
  deployment (R4).
- **Negative:** the decryption key becomes the crown jewels — losing it locks
  the organisation out of its own secrets, and leaking it decrypts the entire
  history, so key custody turns into a business process with named owners;
  adding or removing a person re-encrypts every secret file, so the rotation
  is cheap but never free; and the rule protects history only
  from the day it starts — secrets committed before it are still exposed and
  still need rotation. Because the same mechanism serves production, production
  secrets are encrypted to a named set of people: rotating a production
  credential quickly, or granting a break-glass reader, means touching that
  list, and treating it as friction is how the mechanism gets bypassed —
  operational secret handling beyond this list is the question a proposed
  record takes up
  ([028](./028-operational-secret-handling-has-a-named-owner.md)).
- **Neutral / follow-ups:** the current mechanism is file-level encryption to
  named per-person keys, ciphertext committed per project, and run-time
  automation that generates keys and decrypts at bring-up; any plaintext
  configuration found to carry a real value is moved into the ciphertext rather
  than argued about, which means the line between a dev default and a real
  secret needs a check that flags likely-real values before they reach history.
