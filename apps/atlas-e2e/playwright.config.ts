import { defineConfig } from '@playwright/test';

/**
 * Journeys of the Aurelius Atlas frontend (apps/atlas) for the migration check "user journeys".
 * Run the same suite against both stacks and compare:
 *
 *   E2E_BASE_URL=https://old.example.com/aurelius/atlas/  npx playwright test --output=results-old
 *   E2E_BASE_URL=http://localhost:8080/aurelius/atlas/    npx playwright test --output=results-new
 *
 * Users (Keycloak): E2E_ADMIN_USER / _PASSWORD, E2E_STEWARD_USER / _PASSWORD, E2E_SCIENTIST_USER / _PASSWORD.
 * The expected data is the Aurelius sample data (backend/m4i-atlas-post-install/data/sample_data.zip).
 */
export default defineConfig({
    testDir: './tests',
    timeout: 60_000,
    expect: { timeout: 15_000 },
    retries: 1,
    workers: 1,
    reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }], ['json', { outputFile: 'results.json' }]],
    use: {
        baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:8080/aurelius/atlas/',
        ignoreHTTPSErrors: process.env.E2E_INSECURE === 'true',
        trace: 'retain-on-failure',
        screenshot: 'only-on-failure',
    },
});
