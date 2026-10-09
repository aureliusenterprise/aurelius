# Specification Template

Copy the block below into `N-M-short-slug.md` and fill it in before writing code.

```markdown
# N.M Increment title

- **Status:** planned | in progress | in review | done
- **Pull request:** link
- **Records:** ADR / DD numbers this increment adds or relies on

## Scope

What this increment delivers: endpoints, operations, projects. Then what it explicitly does not
deliver, with the increment that will.

## Semantics

Each rule the behaviour must obey, in plain words, with an id that tests name in
`@pytest.mark.covers(..., rules=["XXX-NN"])`.

| Id     | Rule |
| ------ | ---- |
| XXX-01 |      |

## Java origin

The Atlas classes (2.4.0) whose behaviour this ports, so reviewers can compare.

## Deviations

Deliberate differences from Apache Atlas, each added to [Deviations](../deviations.md).

## Acceptance

The parity scenarios and test files that prove the rules, and how to run them.
```
