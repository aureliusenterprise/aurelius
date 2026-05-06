import {
    HttpEvent,
    HttpEventType,
    HttpHandlerFn,
    HttpInterceptorFn,
    HttpRequest,
    HttpErrorResponse,
} from "@angular/common/http";
import { inject } from "@angular/core";
import { context, propagation, SpanKind, SpanStatusCode, trace } from "@opentelemetry/api";
import { Observable } from "rxjs";
import { tap, finalize } from "rxjs/operators";
import { AURELIUS_TRACER } from "./opentelemetry.provider";

function injectPropagationHeaders(
    request: HttpRequest<unknown>,
    spanContext: ReturnType<typeof context.active>,
): HttpRequest<unknown> {
    const carrier: Record<string, string> = {};
    propagation.inject(spanContext, carrier);

    return Object.entries(carrier).reduce((req, [key, value]) => req.clone({ setHeaders: { [key]: value } }), request);
}

// Exported for testing
export function injectTraceIdHeader(
    request: HttpRequest<unknown>,
    spanContext: ReturnType<typeof context.active>,
): HttpRequest<unknown> {
    const span = trace.getSpan(spanContext);
    const traceId = span?.spanContext().traceId;

    if (!traceId) {
        return request;
    }

    return request.clone({
        setHeaders: {
            "X-Trace-Id": traceId,
        },
    });
}

// Exported for testing
export function setSpanStatusFromEvent(
    span: ReturnType<ReturnType<typeof trace.getTracer>["startSpan"]>,
    event: HttpEvent<unknown>,
): void {
    if (event.type === HttpEventType.Response) {
        span.setAttribute("http.response.status_code", event.status);

        if (event.status >= 400) {
            span.setStatus({ code: SpanStatusCode.ERROR });
        }
    }
}

export const aureliusOpenTelemetryHttpInterceptor: HttpInterceptorFn = (
    request: HttpRequest<unknown>,
    next: HttpHandlerFn,
): Observable<HttpEvent<unknown>> => {
    const tracer = inject(AURELIUS_TRACER);
    const spanName = `${request.method} ${request.url}`;
    const span = tracer.startSpan(spanName, {
        kind: SpanKind.CLIENT,
        attributes: {
            "http.request.method": request.method,
            "url.full": request.url,
        },
    });

    const spanContext = trace.setSpan(context.active(), span);
    const requestWithPropagationHeaders = injectPropagationHeaders(request, spanContext);
    const requestWithTraceHeaders = injectTraceIdHeader(requestWithPropagationHeaders, spanContext);

    return next(requestWithTraceHeaders).pipe(
        tap({
            next: (event) => {
                setSpanStatusFromEvent(span, event);
            },
            error: (error: unknown) => {
                // Capture response status from HttpErrorResponse if available
                if (error instanceof HttpErrorResponse && error.status) {
                    span.setAttribute("http.response.status_code", error.status);
                }
                span.recordException(error instanceof Error ? error : new Error("HTTP request failed"));
                span.setStatus({ code: SpanStatusCode.ERROR });
            },
        }),
        finalize(() => span.end()),
    );
};
