# 0.1 Adopt the template

- **Status:** in review
- **Records:** ADR 046–051, DD-001, DD-002, DV-01, DV-02

## Scope

Turn the Aurelius Project Template into the Aurelius Atlas repository without adding Atlas code:

- Remove the Kafka streaming slice (`aurelius-java-producer-example`, `aurelius-node-red-example`,
  `libs/python/aurelius-kafka`, `connectors/…`, `dev/kafka`), the AWS Lambda slice
  (`aurelius-aws-lambda-example`, `libs/python/aurelius-aws-lambda`, `docker/aurelius-aws-lambda-base`,
  `dev/aws-lambda-rie`), the Java library and the Gradle build, and the Kafka design guide.
- Rename the repository identity to `aurelius-atlas` (root manifests, docs site, devcontainer).
- Record ADRs 046–051 and create this conversion ledger.
- Add the conversion workflow to the root `AGENTS.md` and a pull-request template.

Not in scope: the template's spine examples (FastAPI example, Angular example, `aurelius-example`,
Postgres) stay until increment 0.5 replaces them.

## Semantics

| Id     | Rule                                                                         |
| ------ | ---------------------------------------------------------------------------- |
| ADO-01 | No project, workspace member, Nx plugin or CI step refers to a removed slice |
| ADO-02 | Every remaining project still lints, type-checks and passes its unit tests   |
| ADO-03 | Every new record is reachable from the docs navigation                       |

## Java origin

None.

## Deviations

DV-01 (no notifications), DV-02 (simple authorizer only).

## Acceptance

`uv sync`, `npx nx show projects` without graph errors, `nx run-many -t lint typecheck`, the unit
tests of the remaining Python projects, and `zensical build` for the documentation. The ADO rules are
checked by these commands rather than by dedicated tests; the traceability tooling arrives in 0.3.
