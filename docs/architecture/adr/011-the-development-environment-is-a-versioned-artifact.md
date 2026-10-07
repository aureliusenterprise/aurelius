# 011. The development environment is a versioned artifact

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

The environment that developers work in and the pipeline runs in is built from
a definition held in the repository, not assembled by hand on each machine. It
carries the toolchains, runtimes, and command-line tools the system needs, so
a machine contributing to the system needs only the means to run that
environment.

There is one base, not one variant per operating system. Automation is written
against the base rather than against the estate of machines that run it, so it
does not branch on operating system, runtime, or the tools a machine happens
to have installed.

The definition — not any running copy — is the authoritative thing: the
environment is rebuilt from it whenever it changes, and a running copy carries
no state that the definition cannot reproduce.

## Context

The tooling that builds and validates the system runs on machines the
organisation does not control: the laptops of the people doing the work, and
the pool of machines the pipeline runs on. That tooling has to run on top of
something, and what it runs on differs between those machines unless someone
decides otherwise.

A developer's machine is the least controllable machine in the estate. Its
operating system, runtime versions, and installed tools differ between
machines and drift over time without anyone deciding. Automation written
against that estate spends its effort on the estate: time spent getting a
particular machine to cooperate is time not spent on the system, and a fix
worked out on one machine is not known to help on the next.

The same automation also has to run unattended. A pipeline has no one at a
keyboard to install a missing tool, upgrade a runtime, or explain why the
build behaves differently than it did on a laptop.

The decision to make is what the automation runs on, who owns the differences
between machines, and where the truth about the environment lives.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One base for people and pipelines.** The environment a developer uses
  and the environment the pipeline uses come from the same definition, so a
  result in one is a result in the other.
- **R2 — Machine differences stop at the boundary.** Differences in operating
  system, runtime versions, and installed tools do not reach the automation,
  because the automation sees only the base.
- **R3 — The environment is built, not inherited.** The environment comes from
  a definition in version control, so it can be reviewed, reviewed with the
  change that needed a new tool, and rebuilt anywhere — not inherited from the
  accumulated state of a machine.
- **R4 — Unattended runs need no person.** Reaching the environment is a
  command the pipeline can issue alone; no step waits for someone to install
  or configure something.
- **R5 — Cheap to keep true.** Adding a tool the system needs is an edit to
  the environment definition by the person who needs it, visible in review,
  not a change request to whoever maintains the machines.

## Alternatives

- **Configure every machine to a documented standard.** Keep a setup
  checklist, or a script that prepares a machine, and require everyone to run
  it. It fails R2: the checklist covers what its author thought of, machines
  drift afterwards, and the automation still discovers the differences; it
  fails R4 as well, because preparation is a person's task, repeated per
  machine and per refresh.
- **One environment variant per operating system.** Support each operating
  system with its own variant of the environment. It fails R1 — the base is no
  longer one thing — and multiplies the automation by the number of supported
  platforms, so every change is written and tested once per variant.
- **Rely on the tools a machine already has.** Write the automation against
  whatever interpreters, build tools, and CLIs are present. It fails R1 and
  R2 outright: the base becomes the union of every machine's accidents, and
  the automation carries the differences as conditionals; it fails R3, because
  a clean machine has nothing installed and the pipeline's environment is
  whatever the platform happens to provide.
- **Do nothing (each person prepares their own machine).** Zero cost today. It
  fails R1 by default — every machine is its own environment — and R4 by
  default, because every unattended run inherits the assumptions of whoever
  set up the machine it runs on.

## Tradeoffs

- **Positive:** the automation is written once rather than once per operating
  system and once per toolchain (R1); machine differences stop at the base
  instead of surfacing as defects in the system (R2); a clean machine reaches a
  working environment with one command, which is what makes the unattended
  pipeline and the offline laptop possible at all (R3, R4); adding a tool is a
  reviewed change to one definition (R5).
- **Negative:** the base is a maintained artifact — it must be rebuilt as the
  system's toolchains change, and a stale base produces failures that look
  like application bugs; the base becomes part of every delivery path, so a
  failure to build it stops work everywhere; and tooling that cannot run
  inside the base, or that a machine's policy keeps out, is excluded and needs
  another arrangement.
- **Neutral / follow-ups:** the current form of the base is a container image,
  which is an implementation choice this record survives: replacing the form
  would change the follow-through, not the rule. The base must be rebuilt on a
  stated trigger rather than whenever someone remembers, or drift between the
  definition and the environment in use becomes the difference this record was
  meant to remove; parts that run outside the base — a build tool or an
  emulator invoked directly — deviate from this record until they run through
  it.
