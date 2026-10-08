/**
 * Shape of the runtime configuration served at `/config.json`.
 *
 * This file is fetched at bootstrap and is **not** bundled into the production
 * build (see `build.configurations.development.assets` in `project.json`). Each
 * deployment serves its own `config.json`, so the same image can target any
 * environment.
 */
export interface AppConfig {
    /**
     * Keycloak connection settings for the `keycloak-angular` client.
     */
    readonly keycloak: AppConfigKeycloak;

    /**
     * Base URL that the API is reachable under, same-origin (e.g. `/api`).
     * Provided to `aurelius-data-access` via the `API_BASE_URL` token.
     */
    readonly apiBaseUrl: string;

    /**
     * OTLP trace exporter endpoint, same-origin (e.g. `/otel/v1/traces`).
     */
    readonly otelExporterUrl: string;
}

/**
 * Keycloak client settings within {@link AppConfig}.
 */
export interface AppConfigKeycloak {
    /**
     * The Keycloak client id (public client — safe to expose in the browser).
     */
    readonly clientId: string;

    /**
     * The Keycloak realm name.
     */
    readonly realm: string;

    /**
     * The base URL of the Keycloak server.
     */
    readonly url: string;
}

/**
 * Validate and narrow an unknown value (e.g. parsed JSON) into a typed
 * {@link AppConfig}. Throws a descriptive error when the shape is wrong so a
 * misconfigured deployment fails loudly at bootstrap instead of blank-screening.
 *
 * @param value The parsed `/config.json` payload.
 * @returns The validated {@link AppConfig}.
 * @throws If the payload does not match the expected shape.
 */
export function parseAppConfig(value: unknown): AppConfig {
    if (typeof value !== "object" || value === null) {
        throw new Error("Invalid app config: expected a JSON object.");
    }

    const { keycloak, apiBaseUrl, otelExporterUrl } = value as Partial<AppConfig>;

    if (typeof keycloak !== "object" || keycloak === null) {
        throw new Error('Invalid app config: missing "keycloak" object.');
    }

    const { clientId, realm, url } = keycloak as Partial<AppConfigKeycloak>;

    const requireString = (name: string, field: unknown): string => {
        if (typeof field !== "string" || field.length === 0) {
            throw new Error(`Invalid app config: "${name}" must be a non-empty string.`);
        }
        return field;
    };

    return {
        keycloak: {
            clientId: requireString("keycloak.clientId", clientId),
            realm: requireString("keycloak.realm", realm),
            url: requireString("keycloak.url", url),
        },
        apiBaseUrl: requireString("apiBaseUrl", apiBaseUrl),
        otelExporterUrl: requireString("otelExporterUrl", otelExporterUrl),
    };
}
