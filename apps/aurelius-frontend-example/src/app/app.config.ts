import { provideHttpClient, withInterceptors, withXhr } from "@angular/common/http";
import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from "@angular/core";
import { provideRouter } from "@angular/router";
import { provideApiBaseUrl } from "aurelius-data-access";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { aureliusOpenTelemetryHttpInterceptor, provideAureliusOpenTelemetry } from "aurelius-observability";
import {
    INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
    includeBearerTokenInterceptor,
    provideKeycloak,
} from "keycloak-angular";
import { AppConfig, parseAppConfig } from "./config";
import { routes } from "./routes";

/**
 * Load and validate the runtime configuration served at `/config.json`.
 *
 * Fails loudly (rather than blank-screening) when the file is missing, not
 * reachable, or has the wrong shape.
 * @returns The typed {@link AppConfig}.
 */
async function loadConfig(): Promise<AppConfig> {
    const response = await fetch("/config.json");

    if (!response.ok) {
        throw new Error(`Failed to load app config (/config.json): ${response.status} ${response.statusText}`);
    }

    return parseAppConfig(await response.json());
}

/**
 * Load the application configuration from the server and initialize the application.
 * @returns ApplicationConfig
 */
export async function initialize(): Promise<ApplicationConfig> {
    const config = await loadConfig();

    return {
        providers: [
            provideBrowserGlobalErrorListeners(),
            provideAureliusOpenTelemetry({
                exporter: new OTLPTraceExporter({
                    url: config.otelExporterUrl,
                }),
                name: "aurelius-frontend-example",
            }),
            provideApiBaseUrl(config.apiBaseUrl),
            provideKeycloak({
                config: config.keycloak,
                initOptions: {
                    onLoad: "check-sso",
                    silentCheckSsoRedirectUri: globalThis.location.origin + "/silent-check-sso.html",
                },
            }),
            {
                provide: INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
                useValue: [{ urlPattern: /^.*\/api\/.*$/ }],
            },
            provideRouter(routes),
            provideHttpClient(
                withXhr(),
                withInterceptors([aureliusOpenTelemetryHttpInterceptor, includeBearerTokenInterceptor]),
            ),
            provideZonelessChangeDetection(),
        ],
    };
}
