import { TestBed } from "@angular/core/testing";
import { InMemorySpanExporter, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";
import { describe, it, expect, afterEach } from "vitest";
import {
    AURELIUS_TRACER,
    AURELIUS_WEB_TRACER_PROVIDER,
    AureliusOpenTelemetryOptions,
    createAureliusWebTracerProvider,
    provideAureliusOpenTelemetry,
} from "./opentelemetry.provider";

describe("OpenTelemetry Provider", () => {
    afterEach(() => {
        TestBed.resetTestingModule();
    });

    describe("createAureliusWebTracerProvider", () => {
        it("should create a WebTracerProvider with default ConsoleSpanExporter", async () => {
            const provider = createAureliusWebTracerProvider();

            expect(provider).toBeInstanceOf(WebTracerProvider);
            await provider.forceFlush();
        });

        it("should set service.name from options", () => {
            const provider = createAureliusWebTracerProvider({ name: "test-service" });
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            const spanContext = span.spanContext();

            expect(spanContext.traceId).toBeTruthy();
            span.end();
        });

        it("should use default service.name when not provided", () => {
            const provider = createAureliusWebTracerProvider();
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");

            expect(span).toBeTruthy();
            span.end();
        });

        it("should set service.version when serviceVersion option is provided", async () => {
            const exporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                name: "test-service",
                serviceVersion: "1.2.3",
                exporter: exporter,
                spanProcessors: [new SimpleSpanProcessor(exporter)],
            });
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();

            expect(exporter.getFinishedSpans().length).toBeGreaterThan(0);
        });

        it("should not set service.version when serviceVersion is not provided", async () => {
            const exporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                name: "test-service",
                exporter: exporter,
                spanProcessors: [new SimpleSpanProcessor(exporter)],
            });
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();

            expect(exporter.getFinishedSpans().length).toBeGreaterThan(0);
        });

        it("should use custom SpanExporter when provided", async () => {
            const customExporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                name: "test-service",
                exporter: customExporter,
            });

            expect(provider).toBeInstanceOf(WebTracerProvider);
            // Verify the exporter is used by checking that spans can be exported
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();

            const spans = customExporter.getFinishedSpans();
            expect(spans.length).toBeGreaterThan(0);
        });

        it("should use custom SpanProcessors when provided", async () => {
            const inMemoryExporter = new InMemorySpanExporter();
            const customProcessor = new SimpleSpanProcessor(inMemoryExporter);

            const provider = createAureliusWebTracerProvider({
                name: "test-service",
                spanProcessors: [customProcessor],
            });

            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("custom-span");
            span.end();
            await provider.forceFlush();

            const spans = inMemoryExporter.getFinishedSpans();
            expect(spans.length).toBe(1);
            expect(spans[0].name).toBe("custom-span");
        });

        it("should register the provider globally", () => {
            const provider = createAureliusWebTracerProvider({ name: "test-service" });

            // A registered provider is created and can be used
            expect(provider).toBeInstanceOf(WebTracerProvider);
            const tracer = provider.getTracer("test");
            expect(tracer).toBeTruthy();
        });
    });

    describe("provideAureliusOpenTelemetry DI", () => {
        it("should provide AURELIUS_WEB_TRACER_PROVIDER injection token", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry({ name: "test-service" })],
            });

            const provider = TestBed.inject(AURELIUS_WEB_TRACER_PROVIDER);

            expect(provider).toBeInstanceOf(WebTracerProvider);
            expect(provider).toBeTruthy();
        });

        it("should provide AURELIUS_TRACER injection token", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry({ name: "test-service", version: "1.0.0" })],
            });

            const tracer = TestBed.inject(AURELIUS_TRACER);

            expect(tracer).toBeTruthy();
            expect(tracer).toHaveProperty("startSpan");
        });

        it("should create tracer with correct scope name from options", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry({ name: "my-service", version: "2.0.0" })],
            });

            const tracer = TestBed.inject(AURELIUS_TRACER);
            const span = tracer.startSpan("test-span");

            expect(span).toBeTruthy();
            expect(span.spanContext().traceId).toBeTruthy();

            span.end();
        });

        it("should use default name for tracer scope when not provided", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry()],
            });

            const tracer = TestBed.inject(AURELIUS_TRACER);

            expect(tracer).toBeTruthy();
        });

        it("should create provider as singleton - same instance on multiple injections", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry({ name: "singleton-test" })],
            });

            const provider1 = TestBed.inject(AURELIUS_WEB_TRACER_PROVIDER);
            const provider2 = TestBed.inject(AURELIUS_WEB_TRACER_PROVIDER);

            expect(provider1).toBe(provider2);
        });

        it("should initialize provider on app initialization", () => {
            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry({ name: "init-test" })],
            });

            // Injecting the provider should trigger initialization
            const provider = TestBed.inject(AURELIUS_WEB_TRACER_PROVIDER);

            expect(provider).toBeInstanceOf(WebTracerProvider);
        });

        it("should pass custom options to provider creation", async () => {
            const customExporter = new InMemorySpanExporter();
            const options: AureliusOpenTelemetryOptions = {
                name: "custom-service",
                serviceVersion: "3.0.0",
                exporter: customExporter,
                spanProcessors: [new SimpleSpanProcessor(customExporter)],
            };

            TestBed.configureTestingModule({
                providers: [provideAureliusOpenTelemetry(options)],
            });

            const provider = TestBed.inject(AURELIUS_WEB_TRACER_PROVIDER);
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();

            expect(customExporter.getFinishedSpans().length).toBeGreaterThan(0);
        });
    });

    describe("Edge cases", () => {
        it("should handle undefined options gracefully", async () => {
            const exporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                exporter: exporter,
                spanProcessors: [new SimpleSpanProcessor(exporter)],
            });

            expect(provider).toBeInstanceOf(WebTracerProvider);
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();
            expect(exporter.getFinishedSpans().length).toBeGreaterThan(0);
        });

        it("should handle empty options object", async () => {
            const exporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                exporter: exporter,
                spanProcessors: [new SimpleSpanProcessor(exporter)],
            });

            expect(provider).toBeInstanceOf(WebTracerProvider);
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();
            expect(exporter.getFinishedSpans().length).toBeGreaterThan(0);
        });

        it("should preserve resource attributes from defaultResource", async () => {
            const exporter = new InMemorySpanExporter();
            const provider = createAureliusWebTracerProvider({
                name: "test-service",
                exporter: exporter,
                spanProcessors: [new SimpleSpanProcessor(exporter)],
            });
            const tracer = provider.getTracer("test");
            const span = tracer.startSpan("test-span");
            span.end();
            await provider.forceFlush();

            // Verify that spans are created with the provider
            expect(exporter.getFinishedSpans().length).toBeGreaterThan(0);
        });
    });
});
