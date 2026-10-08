import { EnvironmentProviders, InjectionToken, makeEnvironmentProviders } from "@angular/core";

/**
 * Base URL that the Aurelius API is reachable under, same-origin (e.g. `/api`).
 *
 * Consuming apps provide this from their runtime configuration (see
 * {@link provideApiBaseUrl}); it defaults to `/api` when not provided.
 */
export const API_BASE_URL = new InjectionToken<string>("AURELIUS_API_BASE_URL", {
    providedIn: "root",
    factory: () => "/api",
});

/**
 * Provide the API base URL for the data-access services from an app's runtime
 * configuration.
 *
 * @param apiUrl The base URL the API is reachable under (e.g. `/api`).
 * @returns Environment providers for `appConfig.providers`.
 */
export function provideApiBaseUrl(apiUrl: string): EnvironmentProviders {
    return makeEnvironmentProviders([{ provide: API_BASE_URL, useValue: apiUrl }]);
}
