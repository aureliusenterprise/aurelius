# 007. One shared identity provider serves every authenticated surface

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

One shared identity provider is the only place people exist in the business
system. Every surface that authenticates a human — the screens, the APIs
behind them, the operational tooling — delegates to it: the provider decides
who a person is and whether they are admitted now, and surfaces act only on
what the provider has issued.

Surfaces therefore hold no user accounts, store no credentials, and implement
no sign-in flow. The provider is part of the system, not a service beside it:
it runs wherever the system runs — on an engineer's machine and in the
pipeline — so the authenticated path is exercised everywhere the system is
validated ([006](./006-the-whole-system-runs-on-one-machine.md)), and surfaces
verify tokens against it rather than trusting their own judgement of who is
calling.

## Context

The business system is touched by people in several places: the screens where
work is entered, the APIs behind those screens, the tooling that operates the
system. Each place must know who is acting, and each would, left to itself,
keep its own list of people.

People join, change roles, and leave. When a person leaves, the business must
stop recognising them everywhere at once. With identity held per surface,
revocation is a checklist across every place that kept a user, and its
completeness depends on whoever carries it out.

Access is also audited. Whoever audits asks who could reach what, and when.
One place that answers the question answers the question directly; several
places require their records to be reconciled by hand before the question can
be answered.

Finally, admission is code that has to run to be trusted. A sign-in path that
only exists in production is a path no earlier run has exercised, and
identity code carries the least tolerance for unexercised paths.

The decision to make is where the answer to "who is this person, and are they
in?" lives, and who is allowed to answer it.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One answer about people.** Exactly one authoritative statement of who
  the people are and whether each is admitted; no surface keeps its own list
  or its own verdict.
- **R2 — Revocation is one action.** Ending a person's access at the provider
  ends it at every surface without touching the surfaces, and takes effect on
  the next request, not the next release.
- **R3 — Surfaces stay thin.** A surface stores no credentials, issues no
  tokens, and implements no sign-in flow; it verifies what the provider
  issued. The security-critical code is written, reviewed, and patched once.
- **R4 — Identity runs where validation runs.** The provider is part of the
  system that runs locally and in CI
  ([006](./006-the-whole-system-runs-on-one-machine.md)), so authenticated
  paths are exercised in every validation, not only in production.
- **R5 — The provider is replaceable.** Surfaces integrate through a standard
  interface, so the provider itself can be changed without rewriting the
  surfaces that depend on it.

## Alternatives

- **Per-surface identity.** Each surface keeps its own users and its own
  sign-in. It fails R1 — there are as many answers about people as there are
  surfaces — and R2: revocation becomes a tour of every surface, complete
  only when someone remembers every stop. It fails R3 as well: every surface
  writes its own password handling and session handling, and every one is a
  place a breach can happen.
- **The cloud platform's identity service.** Use the identity service of
  whichever platform runs production. It fails R4: the everyday loop — and
  every unattended run — would reach a service behind a cloud account and a
  network, so the authenticated path cannot be exercised by a machine that is
  offline, or by one whose policy keeps it off the cloud
  ([006](./006-the-whole-system-runs-on-one-machine.md)).
- **A home-grown auth service.** Build the single provider in-house. It can
  deliver R1 and R3 — one provider, thin surfaces — but fails R5: the
  interface is whatever the first surface needed, so replacing or extending it
  is a rewrite, and the credential-handling code becomes permanently the
  organisation's own audit surface.
- **Do nothing (surfaces stay unauthenticated until one needs auth).** Zero
  cost today. It fails R1 by default — the first surface that needs auth
  invents the answer the next surface then inherits — and R4: the admission
  path is exercised for the first time in production, which is where identity
  bugs are least affordable.

## Tradeoffs

- **Positive:** revocation is one action with immediate effect (R2);
  credential and session code exists once, reviewed once, patched once (R3);
  the authenticated path runs on every machine and every pipeline, so auth
  regressions fail a build rather than a user (R4); surfaces speak a standard
  interface, so the provider can be replaced without touching them (R5).
- **Negative:** the provider is critical infrastructure — while it is down,
  every authenticated surface is down, and its availability is now the
  availability of the business system's front door; the local environment
  carries another service to start, version, and keep current; and identity
  is where compliance looks hardest, so where the provider stores user data
  and who administers it are constrained by policy, not preference.
- **Neutral / follow-ups:** the current implementation is a self-hosted
  provider speaking OIDC, with the application registered as a public client;
  every surface that authenticates a human needs the same delegation; and the
  application's registration belongs in a realm of its own rather than in the
  provider's administrative realm. This record covers people only: the
  services that move data and calls between surfaces — the streaming paths and
  service-to-service calls — are not people and are not in its scope; their
  identity is a separate decision
  ([013](./013-services-prove-who-they-are-at-every-boundary.md)).
