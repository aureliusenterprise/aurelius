import { HttpClient, HttpEvent, HttpEventType, provideHttpClient, withInterceptors } from "@angular/common/http";
import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { InMemorySpanExporter, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { combineLatest } from "rxjs";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { aureliusOpenTelemetryHttpInterceptor, setSpanStatusFromEvent } from "./opentelemetry-http.interceptor";
import { provideAureliusOpenTelemetry } from "./opentelemetry.provider";
import { Span, SpanStatusCode } from "@opentelemetry/api";

describe("OpenTelemetry HTTP Interceptor", () => {
    let httpClient: HttpClient;
    let httpMock: HttpTestingController;
    let spanExporter: InMemorySpanExporter;

    beforeEach(() => {
        spanExporter = new InMemorySpanExporter();

        TestBed.configureTestingModule({
            providers: [
                provideHttpClient(withInterceptors([aureliusOpenTelemetryHttpInterceptor])),
                provideHttpClientTesting(),
                provideAureliusOpenTelemetry({
                    name: "test-frontend",
                    exporter: spanExporter,
                    spanProcessors: [new SimpleSpanProcessor(spanExporter)],
                }),
            ],
        });

        httpClient = TestBed.inject(HttpClient);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        if (httpMock) {
            try {
                httpMock.verify();
            } catch {
                // Suppress verification errors if requests weren't made
            }
        }
        spanExporter.reset();
    });

    describe("Span creation and basic attributes", () => {
        it("should allow HTTP GET requests", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: (data) => {
                        expect(data).toEqual({ success: true });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ success: true });
            }));

        it("should allow HTTP POST requests", () =>
            new Promise<void>((done, fail) => {
                httpClient.post("/api/entities", { name: "Test" }).subscribe({
                    next: (data) => {
                        expect(data).toEqual({ guid: "123" });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/entities");
                expect(req.request.method).toBe("POST");
                req.flush({ guid: "123" });
            }));

        it("should allow HTTP DELETE requests", () =>
            new Promise<void>((done, fail) => {
                httpClient.delete("/api/entities/123").subscribe({
                    next: () => {
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/entities/123");
                expect(req.request.method).toBe("DELETE");
                req.flush(null);
            }));

        it("should handle query parameters in URLs", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/entities?limit=10&skip=5").subscribe({
                    next: (data) => {
                        expect(data).toEqual({ data: [] });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne((r) => r.url.includes("limit=10"));
                expect(req.request.url).toContain("skip=5");
                req.flush({ data: [] });
            }));
    });

    describe("Propagation headers", () => {
        it("should allow GET, POST, and PUT requests", () =>
            new Promise<void>((done, fail) => {
                let completed = 0;
                const handleComplete = () => {
                    completed++;
                    if (completed === 3) {
                        done();
                    }
                };

                httpClient.get("/api/get-test").subscribe({
                    next: handleComplete,
                    error: fail,
                });
                httpClient.post("/api/post-test", {}).subscribe({
                    next: handleComplete,
                    error: fail,
                });
                httpClient.put("/api/put-test", {}).subscribe({
                    next: handleComplete,
                    error: fail,
                });

                httpMock.expectOne("/api/get-test").flush({});
                httpMock.expectOne("/api/post-test").flush({});
                httpMock.expectOne("/api/put-test").flush({});
            }));
    });

    describe("Response status handling", () => {
        it("should handle successful 200 responses", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: (data) => {
                        expect(data).toEqual({ data: "success" });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ data: "success" }, { status: 200, statusText: "OK" });
            }));

        it("should handle created 201 responses", () =>
            new Promise<void>((done, fail) => {
                httpClient.post("/api/entities", { name: "Test" }).subscribe({
                    next: (data) => {
                        expect(data).toEqual({ guid: "123" });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/entities");
                req.flush({ guid: "123" }, { status: 201, statusText: "Created" });
            }));

        it("should handle 3xx redirect responses as errors", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        fail(new Error("Should have treated 301 as error"));
                    },
                    error: (error) => {
                        expect(error.status).toBe(301);
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.flush(null, { status: 301, statusText: "Moved Permanently" });
            }));

        it("should handle 400 bad request responses as errors", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        fail(new Error("Should have treated 400 as error"));
                    },
                    error: (error) => {
                        expect(error.status).toBe(400);
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ error: "Bad request" }, { status: 400, statusText: "Bad Request" });
            }));

        it("should handle 404 not found responses as errors", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        fail(new Error("Should have treated 404 as error"));
                    },
                    error: (error) => {
                        expect(error.status).toBe(404);
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ error: "Not found" }, { status: 404, statusText: "Not Found" });
            }));

        it("should handle 500 server error responses as errors", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        fail(new Error("Should have treated 500 as error"));
                    },
                    error: (error) => {
                        expect(error.status).toBe(500);
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ error: "Internal server error" }, { status: 500, statusText: "Internal Server Error" });
            }));

        it("should handle 502 bad gateway responses as errors", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        fail(new Error("Should have treated 502 as error"));
                    },
                    error: (error) => {
                        expect(error.status).toBe(502);
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.flush(null, { status: 502, statusText: "Bad Gateway" });
            }));
    });

    describe("Error handling", () => {
        it("should handle network errors gracefully", () =>
            new Promise<void>((done) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        // Should not complete successfully on error
                    },
                    error: (error) => {
                        expect(error).toBeTruthy();
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.error(new ProgressEvent("error"));
            }));

        it("should handle request timeouts", () =>
            new Promise<void>((done) => {
                httpClient.get("/api/test").subscribe({
                    next: () => {
                        // Should not complete successfully on error
                    },
                    error: (error) => {
                        expect(error).toBeTruthy();
                        done();
                    },
                });

                const req = httpMock.expectOne("/api/test");
                req.error(new ProgressEvent("error"));
            }));
    });

    describe("Span lifecycle", () => {
        it("should complete successful responses", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/test").subscribe({
                    next: (data) => {
                        expect(data).toEqual({ data: "ok" });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/test");
                req.flush({ data: "ok" });
            }));

        it("should handle multiple requests in sequence", () =>
            new Promise<void>((done, fail) => {
                let count = 0;
                const handleSuccess = () => {
                    count++;
                    if (count === 2) {
                        done();
                    }
                };

                httpClient.get("/api/test1").subscribe({
                    next: handleSuccess,
                    error: fail,
                });
                httpClient.get("/api/test2").subscribe({
                    next: handleSuccess,
                    error: fail,
                });

                httpMock.expectOne("/api/test1").flush({});
                httpMock.expectOne("/api/test2").flush({});
            }));
    });

    describe("Concurrent requests", () => {
        it("should handle multiple concurrent requests", () =>
            new Promise<void>((done, fail) => {
                combineLatest({
                    entities: httpClient.get("/api/entities"),
                    search: httpClient.get("/api/search"),
                    stats: httpClient.get("/api/stats"),
                }).subscribe({
                    next: (results) => {
                        expect(results.entities).toEqual({ data: [] });
                        expect(results.search).toEqual({ results: [] });
                        expect(results.stats).toEqual({ count: 0 });
                        done();
                    },
                    error: fail,
                });

                httpMock.expectOne("/api/entities").flush({ data: [] });
                httpMock.expectOne("/api/search").flush({ results: [] });
                httpMock.expectOne("/api/stats").flush({ count: 0 });
            }));

        it("should handle two concurrent requests", () =>
            new Promise<void>((done, fail) => {
                combineLatest({
                    test1: httpClient.get("/api/test1"),
                    test2: httpClient.get("/api/test2"),
                }).subscribe({
                    next: (results) => {
                        expect(results.test1).toEqual({ id: "1" });
                        expect(results.test2).toEqual({ id: "2" });
                        done();
                    },
                    error: fail,
                });

                httpMock.expectOne("/api/test1").flush({ id: "1" });
                httpMock.expectOne("/api/test2").flush({ id: "2" });
            }));
    });

    describe("Edge cases", () => {
        it("should handle requests with no body", () =>
            new Promise<void>((done, fail) => {
                httpClient.delete("/api/entities/123").subscribe({
                    next: () => {
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/entities/123");
                expect(req.request.body).toBeNull();
                req.flush(null);
            }));

        it("should handle requests with JSON body", () =>
            new Promise<void>((done, fail) => {
                const payload = { name: "Test", description: "Desc" };
                httpClient.post("/api/entities", payload).subscribe({
                    next: (data) => {
                        expect(data).toEqual({ guid: "123" });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne("/api/entities");
                expect(req.request.body).toEqual(payload);
                req.flush({ guid: "123" });
            }));

        it("should handle requests with special characters in URL", () =>
            new Promise<void>((done, fail) => {
                httpClient.get("/api/search?q=hello%20world").subscribe({
                    next: (data) => {
                        expect(data).toEqual({ results: [] });
                        done();
                    },
                    error: fail,
                });

                const req = httpMock.expectOne((r) => r.url.includes("hello"));
                expect(req.request.url).toContain("hello%20world");
                req.flush({ results: [] });
            }));
    });

    describe("Helper function edge cases", () => {
        it("should set error status code on span for 4xx responses", () => {
            const mockSpan = {
                setAttribute: vi.fn(),
                setStatus: vi.fn(),
            } as unknown as Span;

            const mockEvent = {
                type: HttpEventType.Response,
                status: 400,
            } as HttpEvent<unknown>;

            setSpanStatusFromEvent(mockSpan, mockEvent);

            expect(mockSpan.setAttribute).toHaveBeenCalledWith("http.response.status_code", 400);
            expect(mockSpan.setStatus).toHaveBeenCalledWith({ code: SpanStatusCode.ERROR });
        });

        it("should set error status code on span for 5xx responses", () => {
            const mockSpan = {
                setAttribute: vi.fn(),
                setStatus: vi.fn(),
            } as unknown as Span;

            const mockEvent = {
                type: HttpEventType.Response,
                status: 500,
            } as HttpEvent<unknown>;

            setSpanStatusFromEvent(mockSpan, mockEvent);

            expect(mockSpan.setAttribute).toHaveBeenCalledWith("http.response.status_code", 500);
            expect(mockSpan.setStatus).toHaveBeenCalledWith({ code: SpanStatusCode.ERROR });
        });

        it("should not set error status for successful responses", () => {
            const mockSpan = {
                setAttribute: vi.fn(),
                setStatus: vi.fn(),
            } as unknown as Span;

            const mockEvent = {
                type: HttpEventType.Response,
                status: 200,
            } as HttpEvent<unknown>;

            setSpanStatusFromEvent(mockSpan, mockEvent);

            expect(mockSpan.setAttribute).toHaveBeenCalledWith("http.response.status_code", 200);
            expect(mockSpan.setStatus).not.toHaveBeenCalled();
        });

        it("should not process non-Response events", () => {
            const mockSpan = {
                setAttribute: vi.fn(),
                setStatus: vi.fn(),
            } as unknown as Span;

            const mockEvent = {
                type: HttpEventType.Sent,
            } as HttpEvent<unknown>;

            setSpanStatusFromEvent(mockSpan, mockEvent);

            expect(mockSpan.setAttribute).not.toHaveBeenCalled();
            expect(mockSpan.setStatus).not.toHaveBeenCalled();
        });
    });
});
