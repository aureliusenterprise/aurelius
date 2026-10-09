# 050. The system carries only the capabilities the catalogue needs

- **Status:** Accepted
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will remove from this codebase every template capability the catalogue does not use: the event
streaming slice, the serverless slice, the Java build, and — once their replacements exist — the
template's example service, example screen, example library and relational database. This is a
named deviation from the template's spine ([002](./002-modules-are-removable-slices.md)): the
catalogue's own server, dashboard and search store become the spine.

## Context

The codebase was created from a template that demonstrates many capabilities at once. Each kept
capability costs build time, dependency updates, security scanning and reader attention, and
suggests to newcomers that it is part of the product. The catalogue needs one HTTP service, one
user interface, one data store ([047](./047-one-search-store-is-the-system-of-record.md)), the
shared identity provider and observability.

## Requirements

- **R1 — What is here is used.** Every project in the repository serves the catalogue or its
  delivery workflow.
- **R2 — Template updates stay mergeable.** The workflow parts of the template (pipeline, quality
  gate, documentation, secrets) stay recognisable so updates can be merged.
- **R3 — Nothing is removed before it is replaced.** The repository builds and its tests pass
  after every removal.

## Alternatives

- **Keep every template slice.** Fails R1: unused code is maintained, scanned and misread.
- **Start from an empty repository and copy the workflow.** Fails R2: template improvements can no
  longer be merged.

## Tradeoffs

- **Positive:** a smaller, honest codebase; faster pipeline; fewer dependency alerts.
- **Negative:** re-adding event streaming later (for example to accept Atlas hook notifications)
  means restoring the slice from the template.
- **Neutral / follow-ups:** increment 0.1 removes the streaming and serverless slices and the Java
  build; increment 0.5 removes the example service, screen, library and relational database when
  the Atlas server and dashboard replace them. Until then those examples remain a named deviation
  under this record.
