import { EnvironmentProviders, InjectionToken, makeEnvironmentProviders, provideAppInitializer } from "@angular/core";
import { Tracer } from "@opentelemetry/api";
import { defaultResource, resourceFromAttributes } from "@opentelemetry/resources";
import { BatchSpanProcessor, ConsoleSpanExporter, SpanExporter, SpanProcessor } from "@opentelemetry/sdk-trace-base";
import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";

export const AURELIUS_WEB_TRACER_PROVIDER = new InjectionToken<WebTracerProvider>("AURELIUS_WEB_TRACER_PROVIDER");
export const AURELIUS_TRACER = new InjectionToken<Tracer>("AURELIUS_TRACER");

export interface AureliusOpenTelemetryOptions {
    exporter?: SpanExporter;
    serviceVersion?: string;
    spanProcessors?: SpanProcessor[];
    name?: string;
    version?: string;
}

function resolveName(options?: AureliusOpenTelemetryOptions): string {
    return options?.name ?? "aurelius-frontend";
}

export function createAureliusWebTracerProvider(options?: AureliusOpenTelemetryOptions): WebTracerProvider {
    const spanProcessors = options?.spanProcessors ?? [
        new BatchSpanProcessor(options?.exporter ?? new ConsoleSpanExporter()),
    ];

    const resource = defaultResource().merge(
        resourceFromAttributes({
            "service.name": resolveName(options),
            ...(options?.serviceVersion ? { "service.version": options.serviceVersion } : {}),
        }),
    );

    const provider = new WebTracerProvider({ resource, spanProcessors });
    provider.register();
    return provider;
}

export function provideAureliusOpenTelemetry(options?: AureliusOpenTelemetryOptions): EnvironmentProviders {
    let provider: WebTracerProvider | undefined;

    return makeEnvironmentProviders([
        provideAppInitializer(() => {
            provider ??= createAureliusWebTracerProvider(options);
        }),
        {
            provide: AURELIUS_WEB_TRACER_PROVIDER,
            useFactory: () => {
                provider ??= createAureliusWebTracerProvider(options);
                return provider;
            },
        },
        {
            provide: AURELIUS_TRACER,
            useFactory: (webTracerProvider: WebTracerProvider) =>
                webTracerProvider.getTracer(resolveName(options), options?.version),
            deps: [AURELIUS_WEB_TRACER_PROVIDER],
        },
    ]);
}
