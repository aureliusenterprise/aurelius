# Change Management

The change management process is designed to ensure that features and fixes are developed, tested, and released
in a controlled and efficient manner. This process follows a structured flow from development through testing,
acceptance, and production deployment.This allows for rapid iteration while maintaining high quality and stability.

## Development

During the development phase, developers work on new features or fixes in their local development environments.
Each developer has their own isolated environment, which allows them to work independently without affecting
others. The development environment is set up as a development container, which includes all necessary tools and
dependencies.

Developers commit their changes to a feature branch in the GitHub repository. This branch is created from the
main branch and is used to isolate the changes until they are ready for review and testing.

## Test

The testing phase is where the new functionality is validated before it is merged into the main branch and made
available for acceptance testing. This phase is crucial for maintaining code quality and ensuring that new
features do not introduce bugs or regressions.

Testing takes place in a dedicated test environment that is set up as a GitHub Actions workflow. This workflow
runs automated checks and tests to ensure that the code meets the project's quality standards.

The following types of testing are performed:

- **Code Quality**: Code is checked for formatting, linting, and other quality metrics.
- **Unit Testing**: Tests individual units of code in isolation to ensure they work correctly.
- **Integration Testing**: Tests the interaction between different units of code to ensure they work together.
- **End-to-End Testing**: Tests the entire system to ensure it works as expected.

When the automated tests pass, the feature branch is ready for peer review. Another developer reviews the code
changes, provides feedback, and approves the pull request. Once approved, the changes are merged into the main
branch.

## Acceptance

Once all required changes are merged into the main branch, the next step is to create a release candidate. A
release candidate is a version of the software that is ready for acceptance testing. This release candidate is
then deployed to a dedicated acceptance environment. Key users and stakeholders can test the new features
and provide feedback before the changes are released to production.

## Production

After acceptance testing is complete and any necessary adjustments have been made, a final release is prepared.
The final release is deployed to the production environment, making the new features and fixes available to all
users.
