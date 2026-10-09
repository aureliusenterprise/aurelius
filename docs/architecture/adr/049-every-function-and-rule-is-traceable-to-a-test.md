# 049. Every function and every specified rule is traceable to a test, and the trace is published

- **Status:** Accepted
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will require that every public function of the catalogue code and every rule in an increment's
specification is named by at least one test, and the pipeline refuses a change that leaves either
uncovered. Every change produces one published test report that shows, per rule and per function,
which tests cover it and whether they passed.

## Context

The conversion produces a large amount of new code in a short time, much of it with machine
assistance, and every change carries two human signatures
([044](./044-every-change-carries-two-human-signatures.md)). Reviewers need to see what a change
proves, not only what it contains. Line coverage alone says that code ran during a test, not that
any test meant to check it, and it says nothing about whether the specified rules were checked.

## Requirements

- **R1 — No untested function.** A public function without a test that names it does not merge.
- **R2 — No unchecked rule.** A rule stated in a specification without a test that names it does
  not merge.
- **R3 — One place to look.** A reviewer opens one report per change and sees results, coverage,
  traceability and parity together.
- **R4 — Cheap to comply.** Declaring what a test covers is one line in the test.

## Alternatives

- **Coverage percentage only.** Fails R1 and R2: incidental execution counts as coverage, and
  rules are invisible.
- **Manual traceability matrix in a document.** Fails R1 and R2 in practice: it drifts from the
  code on the first busy week.
- **Naming conventions (test name contains the function name).** Partly meets R1 but is fragile
  under renames and cannot express rules or several functions per test.

## Tradeoffs

- **Positive:** reviewers get evidence instead of assurances; gaps are found by the pipeline, not
  by users; the report doubles as living documentation of what is done.
- **Negative:** every test carries a declaration, and trivial functions still need a named test;
  the check can be satisfied by a weak test, so review of test quality remains a human job.
- **Neutral / follow-ups:** current implementation: a pytest marker `covers`, a checker run in the
  test pipeline, and an HTML report built from JUnit and coverage results.
