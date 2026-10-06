import type { ShellAdminLink } from '@models4insight/shell';

/** First path segment of a URL path ("/atlas/auth" -> "atlas") */
function firstSegment(path: string): string {
    return path.split('/').find((segment) => segment.length > 0) ?? '';
}

/**
 * The Admin dialog of the header (administrators only): the tools of the tenant this page belongs to, at
 * <origin>/<namespace>/<tenant>/... . The links are built from config.json rather than from the page address, so
 * they are right however the page was reached (e.g. a legacy address without the tenant):
 * - the tenant: config.json `tenant.id` (window.aureliusTenant), else the Keycloak realm (one realm per tenant);
 * - the namespace: the first segment of the Keycloak url (/<namespace>/auth), else of the page address.
 */
export function aureliusAdminLinks(keycloak: { readonly url: string; readonly realm: string }): ShellAdminLink[] {
    const origin = window.location.origin;
    const keycloakUrl = new URL(keycloak.url.replace(/\/?$/, '/'), document.baseURI);
    const namespace = firstSegment(keycloakUrl.pathname) || firstSegment(window.location.pathname);
    const tenant: string = (window as any).aureliusTenant?.id || keycloak.realm;
    const tenantBase = `${origin}/${encodeURIComponent(namespace)}/${encodeURIComponent(tenant)}/`;
    return [
        {
            route: '/search/classifications',
            title: 'admin.classifications.title',
            description: 'admin.classifications.description',
        },
        {
            url: `${keycloakUrl.href}admin/${encodeURIComponent(keycloak.realm)}/console/`,
            title: 'admin.keycloak.title',
            description: 'admin.keycloak.description',
            // the user management of the realm (aurelius-admin tenant grant-admin)
            requires: { clientRoles: { 'realm-management': ['manage-users', 'view-users'] } },
        },
        {
            url: `${tenantBase}kibana/`,
            title: 'admin.kibana.title',
            description: 'admin.kibana.description',
            // as the proxy requires it for the tenant's Kibana (kibana-tenants.conf)
            requires: { realmRoles: ['ROLE_ADMIN'] },
        },
        {
            url: `${tenantBase}atlas2/`,
            title: 'admin.atlas.title',
            description: 'admin.atlas.description',
        },
    ];
}
