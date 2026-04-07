# Testing Strategy

This document defines how testing is planned, executed, and maintained across the workspace.

## Goals

The testing strategy exists to protect customer value while improving delivery throughput.

### Protect customer trust

Testing protects customer trust by reducing defects in critical workflows, lowering incidents related to reliability,
security, and data integrity, and increasing confidence in every production release. This includes preventing:

- **Data corruption** through validation of business logic and database operations
- **Security vulnerabilities** via authentication/authorization testing and input sanitization checks
- **Service outages** by validating system resilience and error handling
- **Regulatory non-compliance** through audit trail verification and data governance tests

### Improve delivery predictability

Testing improves delivery predictability by catching regressions early, establishing clear quality gates for pull
requests and release candidates, and supporting a consistent release cadence across teams.

### Reduce cost of change

Testing reduces the cost of change by surfacing issues earlier—during development rather than production—when
fixes are faster and less expensive. This lowers rework from escaped defects and shortens investigation time through
reliable, repeatable feedback.

### Enable developer productivity

Testing enables developer productivity by reducing cognitive load for contributors, providing fast local feedback
loops, and minimizing friction in the development workflow. Well-structured tests serve as living documentation
that clarifies expected behavior and reduces the time spent understanding system functionality.

### Enable scalable team execution

Testing enables scalable team execution by standardizing expectations across projects, making onboarding easier
through clear conventions, and supporting parallel development with confidence in integration boundaries.

## Metrics and indicators

The testing strategy should improve the following indicators over time.

!!! NOTE "Business-aligned quality"

    Test coverage is a means, not the end goal. The primary objective is reliable business outcomes: stable
    releases, fewer incidents, and faster delivery.

### Key performance indicators

| Indicator                   | Desired direction | Example target | Business intent                                                                       |
| --------------------------- | ----------------- | -------------- | ------------------------------------------------------------------------------------- |
| Change failure rate (CFR)   | Down              | < 15%          | Reduce release risk and increase confidence in delivery.                              |
| Mean time to restore (MTTR) | Down              | < 1 hour       | Reduce customer and operational impact when failures occur.                           |
| Lead time for changes       | Down              | < 7 days       | Improve speed and predictability of delivery from start of development to production. |

!!! INFO "About the indicators"

    The above indicators are based on the [DORA metrics](https://www.devops-research.com/research.html), which
    are widely recognized as key measures of software delivery performance.

    Example targets are provided as starting points. Actual targets should be operationalized in the context of team goals together
    with business stakeholders during implementation.

??? NOTE "Measurement methodology"

    - **Change failure rate**: Calculated from deployment logs and incident tracking systems (e.g., failed deployments / total deployments)
    - **Mean time to restore**: Measured from incident detection to service restoration, tracked in the incident management system
    - **Lead time for changes**: Tracked from commit to production deployment using CI/CD pipeline metadata

### Supporting leading indicators

Leading indicators provide early warning signals before customer-facing impact:

| Indicator                               | Desired direction | Purpose                                                |
| --------------------------------------- | ----------------- | ------------------------------------------------------ |
| Pull request quality gate pass rates    | Upward / stable   | Early detection of integration issues                  |
| Flaky test rate                         | Downward          | Maintain CI reliability and trust                      |
| Mean time to fix flaky tests            | Downward          | Reduce test debt and improve feedback speed            |
| Recurring regression incidents          | Downward          | Improve test coverage for previously failing scenarios |
| Test execution time (unit layer)        | Stable / downward | Ensure fast local feedback loops                       |
| Test execution time (integration layer) | Stable / downward | Maintain CI pipeline efficiency                        |
| Coverage of critical business paths     | Upward            | Prioritize testing on high-value functionality         |
| Percentage of changes with test updates | Upward            | Maintain confidence as the codebase evolves            |

## Approach

The strategy supports these goals through consistent patterns and tooling that provide fast local feedback for
contributors, reliable validation of cross-service behavior, and predictable CI execution for pull requests and
releases.

To achieve this, our testing model follows a testing pyramid:

- **Unit tests**: high volume, fast execution, isolated behavior
- **Integration tests**: medium volume, service boundaries, realistic dependencies
- **End-to-end (E2E) tests**: focused volume, critical user and data workflows

### Unit tests

Unit tests validate individual functions, classes, and modules in isolation.

Use unit tests to verify business logic quickly, lock in behavior for edge cases and regressions, and refactor
safely with immediate feedback. Unit tests should be deterministic and independent, run in milliseconds to low
seconds, and avoid real network or infrastructure dependencies.

### Integration tests

Integration tests validate interactions between components and external systems.

Use integration tests to confirm API to database behavior, validate messaging flows and service contracts, and
verify configuration and startup assumptions. These tests should run against realistic, typically containerized,
infrastructure with explicit setup and teardown boundaries and focused assertions at integration points.

??? TIP "Contract testing"

    For microservice architectures, consider adding contract testing as an extension of integration tests to validate:

    - API schema compatibility between services
    - Message format consistency across service boundaries
    - Backward compatibility guarantees during version changes

### End-to-end (E2E) tests

E2E tests validate complete workflows across system boundaries.

Use E2E tests to verify user-critical paths from entry to outcome, validate end-to-end data consistency, and confirm
deployment-like behavior before release. Compared to unit and integration tests, E2E suites should remain smaller
due to higher runtime cost, with strong emphasis on reliability and low flake rate.

## Language and framework standards

### Python

Unit and integration tests use [`pytest`](https://docs.pytest.org/en/stable/).

??? INFO "Recommended pytest plugins"

    - [`pytest-cov`](https://github.com/pytest-dev/pytest-cov) - Coverage reporting
    - [`pytest-xdist`](https://github.com/pytest-dev/pytest-xdist) - Parallel test execution
    - [`pytest-mock`](https://github.com/pytest-dev/pytest-mock) - Mocking support

??? INFO "Test naming convention"

    Test files should be named `test\_\_\*.py` (e.g., `test__entity_producer.py`). Test functions should follow the pattern
    `test__<function_name>_<scenario>` for unit tests and `test__<function_name>_<scenario>_<expected_outcome>` for integration
    tests to clarify intent and expected results.

??? INFO "Fixture best practices"

    - Use function-scoped fixtures (`@pytest.fixture()`) for mutable state
    - Use session-scoped fixtures only for expensive shared infrastructure (e.g., database connections, containerized
    services)
    - Prefer parametrized fixtures for testing multiple scenarios without duplication

??? EXAMPLE "Parametrized tests"

    Use `@pytest.mark.parametrize` to test multiple input and expected output combinations without duplicating test code:

    ```python
    @pytest.mark.parametrize("input_value,expected_output", [
        ("valid", "result1"),
        ("invalid", "error"),
    ])
    def test_function(input_value, expected_output):
        ...
    ```

### Angular

Unit tests use [Jest](https://jestjs.io/) or [Vitest](https://vitest.dev/). Choose Jest for broader ecosystem
support and Vitest for faster execution in Vite-based projects.

??? INFO "File naming convention"

    Test files should be named `*.spec.ts` (e.g., `entity-producer.service.spec.ts`) and placed alongside the
    implementation file for easy navigation.

??? INFO "Describe block organization"

    Organize related behavior with describe blocks, limiting nesting to a maximum of 3 levels for readability:

    ```typescript
    describe("UserService", () => {
        describe("when authenticated", () => {
            describe("#getUser", () => {
                it("should return user data", () => { ... });
            });
        });
    });
    ```

??? INFO "Behavior naming convention"

    Use `should <condition> when <scenario>` pattern:

    - `should display error message when form is invalid`
    - `should navigate to dashboard after successful login`

??? INFO "Mocking best practices"

    - Use shallow mocks for service dependencies (mock only the methods being tested)
    - Use deep mocks sparingly, as they can hide integration issues
    - Isolate HTTP behavior using test-time mocks via HttpClientTestingModule

### Java

Unit tests use [JUnit 5](https://junit.org/).

??? INFO "File naming convention"

    Test files should be named `*Test.java` (e.g., `EntityProducerTest.java`). Package structure should mirror the main codebase for easy navigation (e.g., `src/test/java/com/aurelius/producer/`).

??? INFO "Assertion style"

    Prefer `AssertJ` for fluent assertions over built-in JUnit assertions or Hamcrest:

    ```java
    assertThat(entity.getName()).isEqualTo("Test Entity");
    assertThatThrownBy(() -> entity.setGuid(null))
        .isInstanceOf(NullPointerException.class);
    ```

??? INFO "Mockito usage"

    Use [Mockito](https://site.mockito.org/) for isolation and interaction verification:

    - `@Mock` for creating mock dependencies
    - `@InjectMocks` for injecting mocks into the test subject
    - `verify()` for interaction verification

??? INFO "Test isolation patterns"

    - Use `@BeforeEach` to set up fresh state for each test
    - Use `@AfterEach` to clean up any modifications made during tests
    - Avoid static mutable state that can cause test interference

??? EXAMPLE "Parameterized tests"

    Use `@ParameterizedTest` with various sources:

    ```java
    @ParameterizedTest
    @ValueSource(strings = { "valid", "also-valid" })
    void testValidation(String input) {
        assertThat(isValid(input)).isTrue();
    }
    ```

### Testcontainers

For integration and end-to-end testing, use [Testcontainers](https://www.testcontainers.org/) as the default
approach for provisioning dependent services.

??? TIP "Benefits of Testcontainers"

    Prefer ephemeral, containerized dependencies over shared static environments for integration tests. This provides:

    - Isolation: Each test gets a fresh environment, reducing flakiness from shared state.
    - Realism: Tests run against actual service images, improving confidence in production-like behavior.
    - Flexibility: Easily configure different versions and setups for testing various scenarios.

??? TIP "Validating containerized applications"

    Consider running containerized applications in a Testcontainers-managed container during testing. This provides
    higher confidence that the tested behavior matches production-like conditions, including configuration,
    environment variables, and network interactions.

??? EXAMPLE "Multi-service scenarios with Docker Compose"

    Use `DockerCompose` from `testcontainers.compose` when multiple services are required.

    ```python
    from pathlib import Path
    from testcontainers.compose import DockerCompose

    @pytest.fixture(scope="session")
    def compose() -> Generator[DockerCompose]:
        """Return a Docker Compose instance."""
        context = Path(__file__).parent.absolute()
        with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
            yield compose
    ```

??? EXAMPLE "Wait strategies"

    Use appropriate wait strategies for common services. The codebase uses `HealthcheckWaitStrategy`
    for services with health checks defined in Docker Compose.

    ```python
    from pathlib import Path
    from testcontainers.compose import DockerCompose

    @pytest.fixture(scope="session")
    def compose() -> Generator[DockerCompose]:
        """Return a Docker Compose instance."""
        context = Path(__file__).parent.absolute()
        with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
            yield compose.waiting_for(
                {
                    "aurelius-fastapi-example": HealthcheckWaitStrategy(),
                },
            )
    ```

??? EXAMPLE "Service discovery"

    Use `get_service_host_and_port()` or `get_service_port()` to retrieve runtime connection details:

    ```python
    hostname, port = compose.get_service_host_and_port("postgres-app", settings.database_port)

    if not (hostname and port):
        raise ValueError("PostgreSQL service not found in Docker Compose")
    ```

??? EXAMPLE "Log capture"

    Containers are automatically torn down when exiting the context manager. The `capture_docker_compose_logs()`
    helper ensures logs are captured for debugging:

    ```python
    from aurelius_sdk.testing import capture_docker_compose_logs

    with DockerCompose(context=context) as compose:
        yield compose.waiting_for({"service": HealthcheckWaitStrategy()})
        capture_docker_compose_logs(compose)
    ```

### Playwright

For frontend end-to-end testing, use [Playwright](https://playwright.dev/) to validate functional behavior and
critical user flows. The codebase uses Playwright with pytest integration via `playwright.sync_api`.

??? EXAMPLE "Basic assertion"

    Use Playwright's built-in assertions for common checks:

    ```python
    from playwright.sync_api import Page, expect

    def test_main_page_has_welcome_message(authenticated: Page) -> None:
        expect(authenticated.get_by_text(re.compile("Welcome"))).to_be_visible()
    ```

??? EXAMPLE "Authentication fixture"

    The codebase uses pytest fixtures to handle authentication before tests run. A typical authenticated fixture navigates to the app and performs Keycloak login:

    ```python
    @pytest.fixture()
    def authenticated(page: Page, base_url: str, settings: Settings) -> Page:
        """Authenticate the user and return the page."""
        page.goto(base_url)

        # Navigate to Keycloak login
        page.wait_for_url(re.compile(f"/realms/{settings.auth_realm_name}/protocol/openid-connect/auth"))

        # Fill credentials and sign in
        page.locator("#username").fill(settings.username)
        page.locator("#password").fill(settings.password.get_secret_value())
        page.get_by_role("button", name="Sign in").click()

        # Wait for redirect back to app
        page.wait_for_url(re.compile(base_url))

        return page
    ```

??? EXAMPLE "Locator patterns"

    Use semantic locators (test IDs, labels, roles) for more resilient tests:

    - `page.locator("#search-input")` - ID-based locator
    - `page.get_by_role("button", name="Sign in")` - ARIA role-based locator
    - `page.get_by_text(re.compile("Welcome"))` - Text-based locator with regex

??? EXAMPLE "Assertions"

    Common assertion patterns used in the codebase:

    ```python
    # Visibility check
    expect(search_input).to_be_visible()

    # Attribute check
    expect(search_input).to_have_attribute("placeholder", "Search for an entity")

    # Count check
    expect(authenticated.locator(".search-result-card")).to_have_count(len(entities))

    # Text content check
    expect(
        authenticated.get_by_text(re.compile(f"I have found {len(entities)} entities"))
    ).to_be_visible()
    ```

??? TIP "Test isolation"

    Each test should receive a fresh `Page` instance through the fixture, ensuring tests don't interfere with each other. The `authenticated` fixture handles login state separately from individual test logic.

### Chromatic

For visual testing of UI components, use [Chromatic](https://www.chromatic.com/) to catch regressions in shared
UI components and maintain visual consistency. The visual review workflow also allows for non-technical stakeholders
to triage and approve visual changes.

#### Review workflow

Define who approves visual changes based on component type:

- **Design system components**: Require designer approval
- **Feature components**: Developer approval sufficient for non-breaking changes
- **Layout changes**: PM and designer review required

#### Integration with Storybook

Chromatic integrates directly with [Storybook](https://storybook.js.org/) to automatically capture component states.
Ensure all stories are documented and represent actual usage patterns in the application.

!!! SUCCESS "Best practices reinforcement"

    The Chromatic visual testing workflow together with Storybook reinforces best practices around component isolation and documentation in the project.

## Naming and organization conventions

| Language | Test file pattern | Test function pattern                |
| -------- | ----------------- | ------------------------------------ |
| Python   | `test\_\_\*.py`   | `test\_\_<function_name>_<scenario>` |
| Angular  | `\*.spec.ts`      | `should <behavior> when <condition>` |
| Java     | `\*Test.java`     | `test<Method>_<scenario>_<outcome>`  |

General organization rules:

1. Keep tests independent and order-agnostic.
2. Use behavior-oriented names that describe intent.
3. Follow [Arrange, Act, Assert (AAA)](https://semaphore.io/blog/aaa-pattern-test-automation) structure.
4. Prefer reusable fixtures/builders over copy-pasted setup.

## Test data and environment management

Quality and stability depend on disciplined environment control.

Use environment variables and typed settings for configuration, create test data through fixtures or factories
rather than manual shared state, clean up generated data after each test or fixture scope, and avoid hidden dependencies
between test modules.

!!! TIP "Fixture scopes"

    Use session-scoped fixtures only for expensive shared infrastructure.
    Use function-scoped fixtures for mutable state.

## CI/CD integration

Testing is orchestrated with [Nx](https://nx.dev/) and executed in GitHub Actions.

### Nx integration

Nx provides task orchestration across projects, affected-project execution for efficient pull request validation,
task caching to reduce repeated work, and parallel execution for independent tasks.

### Core commands

Use these commands during development and CI troubleshooting:

```bash
# Test one project
nx test <project-name>

# Run E2E for one project
nx e2e <project-name>

# Test affected projects
nx affected -t test e2e -c ci

# Run test target across many projects
nx run-many -t test
```

### CI pipeline expectations

CI validation includes:

1. Runtime and dependency setup (Java, Python, Node.js)
2. Lint/format and pre-commit quality gates
3. Affected test and E2E execution
4. Browser setup for frontend E2E
5. Visual regression checks where configured

!!! NOTE "Merge criteria"

    Pull requests are expected to pass all required affected test stages
    before merge.

## Reliability and maintenance

### Flaky test management

When a test is flaky, follow this sequence:

1. Identify recurring failure patterns in CI.
2. Investigate root causes (timing, isolation, environment).
3. Fix underlying issues before considering retries.
4. Document known flake status and ownership.

### Ongoing maintenance

Maintain test quality by reviewing coverage trends regularly, removing redundant or low-value tests, refactoring
duplicated setup logic, and updating tests as contracts and dependencies evolve.

## Contributor checklist

Before opening a pull request, confirm that:

- New behavior is covered at the correct test layer
- Existing tests were updated for changed contracts
- Affected project tests pass locally
- Any new infrastructure requirements are documented.
