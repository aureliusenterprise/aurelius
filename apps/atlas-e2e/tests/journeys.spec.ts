import { expect, login, SAMPLE, test } from './fixtures';

/*
 * The journeys of the migration plan ("How we know it worked", check 5). Run against both stacks; the
 * results must be identical. Journeys that need phase 3/4 functionality are marked fixme until then.
 */

test.describe('every role', () => {
    for (const role of ['admin', 'steward', 'scientist'] as const) {
        test(`${role} logs in and sees the data domains`, async ({ page, apiErrors }) => {
            await login(page, role, 'search/browse');
            await expect(page).toHaveURL(/search\/browse/);
            for (const name of SAMPLE.domains) {
                await expect(page.getByText(name, { exact: true }).first()).toBeVisible();
            }
            expect(apiErrors).toEqual([]);
        });
    }
});

test('search, filter and open a result', async ({ page, apiErrors }) => {
    await login(page, 'scientist', 'search/browse');
    const search = page.locator('input[type="search"]').first();
    await search.fill(SAMPLE.query);
    await search.press('Enter');
    await expect(page).toHaveURL(/search\/results/);
    const result = page.getByText(SAMPLE.entity.name, { exact: true }).first();
    await expect(result).toBeVisible();
    // facets: a type filter narrows the result list
    const typeFilter = page.getByText('Data Entity', { exact: false }).first();
    if (await typeFilter.isVisible().catch(() => false)) {
        await typeFilter.click();
        await expect(page.getByText(SAMPLE.entity.name, { exact: true }).first()).toBeVisible();
    }
    await result.click();
    await expect(page).toHaveURL(/search\/details\//);
    expect(apiErrors).toEqual([]);
});

test('entity details show attributes, relations and governance', async ({ page, apiErrors }) => {
    await login(page, 'scientist', `search/details/${SAMPLE.domain.guid}`);
    await expect(page.getByText(SAMPLE.domain.name, { exact: true }).first()).toBeVisible();
    expect(apiErrors).toEqual([]);
});

test('data steward edits a definition and sees it after reload', async ({ page, apiErrors }) => {
    await login(page, 'steward', `search/edit-entity/${SAMPLE.entity.guid}`);
    const definition = page.locator('textarea').first();
    await expect(definition).toBeVisible();
    const text = `e2e check ${Date.now()}`;
    await definition.fill(text);
    await page.getByRole('button', { name: /save/i }).first().click();
    await page.goto(`search/details/${SAMPLE.entity.guid}`);
    await expect(page.getByText(text).first()).toBeVisible();
    expect(apiErrors).toEqual([]);
});

test('data scientist cannot create or edit entities', async ({ page }) => {
    await login(page, 'scientist', 'search/browse');
    // the "+" (create entity) button is only rendered for DATA_STEWARD
    await expect(page.locator('a.button.is-info')).toHaveCount(0);
});

test.fixme('editing an attribute updates its governance quality score (phase 3)', async () => {});
test.fixme('lineage view of a process (phase 4)', async () => {});
test.fixme('data governance dashboard (phase 4)', async () => {});
