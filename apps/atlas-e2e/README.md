# atlas-e2e

Browser journeys for `apps/atlas` (Playwright). They are check 5 ("user journeys") of the pyatlas migration
plan: run the same suite against the old stack (Apache Atlas + Flink) and the new one (pyatlas) with the
Aurelius sample data loaded, and compare the results.

```bash
cd apps/atlas-e2e
npm install && npx playwright install chromium     # or use the Docker image below
E2E_BASE_URL=http://localhost:8080/aurelius/atlas/ \
E2E_ADMIN_USER=... E2E_ADMIN_PASSWORD=... \
E2E_STEWARD_USER=... E2E_STEWARD_PASSWORD=... \
E2E_SCIENTIST_USER=... E2E_SCIENTIST_PASSWORD=... npx playwright test
```

On Windows: copy `e2e.env.example` to `e2e.env`, fill it in and run `run_e2e.bat old` (then `run_e2e.bat new`
once pyatlas serves the frontend, phase 1). Without Node on other systems:

```bash
docker run --rm -it -v "$PWD:/e2e" -w /e2e --env-file e2e.env mcr.microsoft.com/playwright:v1.47.2-jammy \
  sh -c "npm install --no-audit --no-fund && npx playwright test"
```

Selectors use the routes (`search/browse`, `search/results`, `search/details/<guid>`, `search/edit-entity/<guid>`),
visible text of the sample data and the standard Keycloak login form. They were written against the Angular
sources and still have to be run once against the current stack (phase 1) — adjust selectors there, so both
stacks are measured with the same, proven suite. The editor journey changes a definition in the sample data.
