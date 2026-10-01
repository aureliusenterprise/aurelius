import type { ShellAdminLink } from '@models4insight/shell';

/**
 * The Admin dialog of the header (administrators only): the tools of the tenant this page belongs to. Computed
 * when the dialog opens, from the page's own address (/<namespace>/<tenant>/atlas/) and the tenant's Keycloak
 * settings of config.json (url /<namespace>/auth, realm = tenant).
 */
export function aureliusAdminLinks(keycloak: { readonly url: string; readonly realm: string }): ShellAdminLink[] {
    // the tenant's base address /<namespace>/<tenant>/ (the frontend is served at <base>atlas/)
    const tenantBase = new URL('../', document.baseURI).href;
    const keycloakBase = new URL(keycloak.url.replace(/\/?$/, '/'), document.baseURI).href;
    return [
        {
            url: `${keycloakBase}admin/${encodeURIComponent(keycloak.realm)}/console/`,
            title: 'admin.keycloak.title',
            description: 'admin.keycloak.description',
        },
        {
            url: `${tenantBase}kibana/`,
            title: 'admin.kibana.title',
            description: 'admin.kibana.description',
        },
        {
            url: `${tenantBase}atlas2/`,
            title: 'admin.atlas.title',
            description: 'admin.atlas.description',
        },
    ];
}
