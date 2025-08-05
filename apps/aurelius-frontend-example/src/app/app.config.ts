import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from "@angular/core";
import { provideRouter } from "@angular/router";
import {
    INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
    includeBearerTokenInterceptor,
    provideKeycloak,
} from "keycloak-angular";
import { routes } from "./routes";

/**
 * Load the application configuration from the server and initialize the application.
 * @returns ApplicationConfig
 */
export async function initialize(): Promise<ApplicationConfig> {
    const { keycloak } = await fetch("/config.json").then((res) => res?.json());

    return {
        providers: [
            provideBrowserGlobalErrorListeners(),
            provideKeycloak({
                config: keycloak,
                initOptions: {
                    onLoad: "check-sso",
                    silentCheckSsoRedirectUri: window.location.origin + "/silent-check-sso.html",
                },
            }),
            {
                provide: INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
                useValue: [{ urlPattern: /^.*\/api\/.*$/ }],
            },
            provideRouter(routes),
            provideHttpClient(withInterceptors([includeBearerTokenInterceptor])),
            provideZoneChangeDetection({ eventCoalescing: true }),
        ],
    };
}
