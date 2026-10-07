# Change Management

The change management process ensures that features and fixes are developed,
tested, and released in a controlled and efficient manner. It follows a
structured flow from development through testing to a release, and hands the
released version to the environments a project or customer operates.

The environments the system itself operates are two: **development**, which is
each person's own machine, and **test**, which is the pipeline. Acceptance and
production are not operated by the system; they exist per engagement, and the
release hands over an artifact complete enough for a deployment to promote
from. The reasoning behind that split is recorded in
[ADR 024](../../adr/024-a-validated-release-is-promoted-by-a-declared-path.md).

## Development

During the development phase, developers work on new features or fixes in
their local development environments. Each developer has their own isolated
environment, which allows them to work independently without affecting
others. The development environment is set up as a development container,
which includes all necessary tools and dependencies, and runs the whole system
— the application and the infrastructure it depends on — on the developer's
machine.

Developers commit their changes to a feature branch in the GitHub repository.
This branch is created from the main branch and is used to isolate the changes
until they are ready for review and testing.

## Test

The testing phase is where the new functionality is validated before it is
merged into the main branch. This phase is crucial for maintaining code
quality and ensuring that new features do not introduce bugs or regressions.

Testing takes place in the test environment: the GitHub Actions pipeline. This
environment runs automated checks and tests to ensure that the code meets the
project's quality standards.

The following types of testing are performed:

- **Code Quality**: Code is checked for formatting, linting, and other quality metrics.
- **Unit Testing**: Tests individual units of code in isolation to ensure they work correctly.
- **Integration Testing**: Tests the interaction between different units of code to ensure they work together.
- **End-to-End Testing**: Tests the entire system against real services, not substitutes.

When the automated tests pass, the feature branch is ready for peer review.
Another developer reviews the code changes, provides feedback, and approves
the pull request. Once approved, the changes are merged into the main branch.

## Release

A version of the system is released as one versioned whole: one number, one
changelog, and one release event that publishes every deployable part together
as signed, provenance-bearing artifacts. Passing the test environment is what
qualifies a change to be part of a release.

## Acceptance and Production

What happens to a released version beyond the pipeline is decided per project
or customer, because acceptance and production are where an engagement's own
requirements live — who signs off, on what environment, under what schedule.
The system's obligation to those environments is the hand-over: a released
artifact that is signed, versioned, and configured only through the settings
the environment supplies, so a deployment can promote it, and roll it back,
without knowledge that lives only with the people who built it.

A project that wants promotion to acceptance and production to be a declared,
repeatable path writes that path against the released artifacts, as part of
its own deployment arrangement.
