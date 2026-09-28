import { expect, Page, test as base } from '@playwright/test';

export type Role = 'admin' | 'steward' | 'scientist';

/** Known content of the Aurelius sample data (atlas-dev.json / sample_data.zip). */
export const SAMPLE = {
    domain: { guid: 'd56db187-2627-41a6-8698-f74d4b76227e', name: 'Personnel and Organization' },
    entity: { guid: '8238db6d-5b6f-486e-9ede-336ddf4694e7', name: 'Customer Order' },
    domains: ['plant data', 'Logistics', 'Finance', 'Procurement'],
    query: 'order',
};

function credentials(role: Role): { user: string; password: string } {
    const key = role.toUpperCase();
    const user = process.env[`E2E_${key}_USER`];
    const password = process.env[`E2E_${key}_PASSWORD`];
    if (!user || !password) {
        base.skip(true, `E2E_${key}_USER / E2E_${key}_PASSWORD not set`);
    }
    return { user: user as string, password: password as string };
}

/** Opens the app and logs in through the Keycloak login page (standard Keycloak form ids). */
export async function login(page: Page, role: Role, path = ''): Promise<void> {
    const { user, password } = credentials(role);
    await page.goto(path);
    const username = page.locator('#username');
    if (await username.isVisible({ timeout: 20_000 }).catch(() => false)) {
        await username.fill(user);
        await page.locator('#password').fill(password);
        await page.locator('#kc-login').click();
    }
    await expect(page).not.toHaveURL(/\/protocol\/openid-connect\//);
}

/** Records failed API calls of the page; every journey asserts that there were none. */
export const test = base.extend<{ apiErrors: string[] }>({
    apiErrors: async ({ page }, use) => {
        const errors: string[] = [];
        page.on('response', (r) => {
            const u = r.url();
            const api = /\/atlas\/(atlas|elastic|data_quality|gov_quality|lineage_model|lineage|api|validate_entity)\b/.test(u);
            if (api && r.status() >= 400) {
                errors.push(`${r.status()} ${r.request().method()} ${u}`);
            }
        });
        await use(errors);
    },
});

export { expect };
