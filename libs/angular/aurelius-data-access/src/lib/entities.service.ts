import { HttpClient } from "@angular/common/http";
import { inject, Injectable, OnDestroy } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { SseClient } from "ngx-sse-client";
import { catchError, EMPTY, filter, map, Observable, Subject } from "rxjs";

export type Envelope<T> = {
    /**
     * The unique identifier for the entity, typically used for tracking updates and deletions.
     */
    readonly guid: string;

    /**
     * The actual data of the entity, which can be null if the entity has been deleted.
     */
    readonly value: T | null;
};

export type Entity = {
    /**
     * The unique identifier for the entity.
     */
    readonly guid?: string | null;

    /**
     * The timestamp when the entity was created, in ISO 8601 format. This field is read-only and set by the server when the entity is created. It may be empty if the entity has not been persisted yet.
     */
    readonly time_created?: string | null;

    /**
     * The timestamp when the entity was last modified, in ISO 8601 format. This field is read-only and updated by the server whenever the entity is updated. It may be empty if the entity has not been modified yet.
     */
    readonly time_modified?: string | null;

    /**
     * The name of the entity.
     */
    name?: string | null;

    /**
     * The description of the entity.
     */
    description?: string | null;
};

export type FindAllQueryParams = {
    /**
     * The maximum number of entities to return.
     */
    limit?: number;

    /**
     * The search query to filter entities by name or description.
     */
    search?: string;

    /**
     * The number of entities to skip for pagination.
     */
    skip?: number;
};

export type PaginatedResponse<T> = {
    /**
     * The total number of entities that match the query, regardless of pagination.
     */
    total: number;

    /**
     * The list of entities returned for the current page.
     */
    data: T[];
};

/**
 * Filters out any query parameters that have falsy values (except for boolean false) to ensure that only valid parameters are sent to the API.
 * @param params The query parameters to filter.
 * @returns A new object containing only the valid query parameters.
 */
function filterParams(params: FindAllQueryParams): FindAllQueryParams {
    return Object.fromEntries(Object.entries(params).filter(([, value]) => typeof value == "boolean" || !!value));
}

/**
 * Type guard to check if an event is a MessageEvent containing entity data. This is used to ensure that we only process relevant events from the SSE stream.
 * @param event The event to check.
 * @returns True if the event is a MessageEvent with string or null data, false otherwise.
 */
function isEntityEvent(event: Event): event is MessageEvent<string | null> {
    return event.type === "entity";
}

/**
 * Parses a MessageEvent containing entity data into an Envelope<Entity> object. This function assumes that the event data is a JSON string that can be deserialized into the expected format. If the event data is null or cannot be parsed, an error is thrown.
 * @param event The MessageEvent to parse.
 * @returns An Envelope<Entity> object containing the parsed entity data.
 * @throws An error if the event data is null or cannot be parsed as JSON.
 */
function parseEntityEvent(event: MessageEvent<string | null>): Envelope<Entity> {
    if (!event.data) {
        throw new Error("Received null data for entity event");
    }
    return JSON.parse(event.data) as Envelope<Entity>;
}

@Injectable({
    providedIn: "root",
})
export class EntitiesService implements OnDestroy {
    /**
     * An observable stream of entity updates received from the server.
     */
    readonly entities$ = new Subject<Envelope<Entity>>();

    /**
     * The HTTP client for making API requests.
     */
    private readonly httpClient = inject(HttpClient);

    /**
     * The SSE client for subscribing to server-sent events.
     */
    private readonly sseClient = inject(SseClient);

    /**
     * Initialize the service by setting up the SSE stream for entity updates.
     */
    constructor() {
        this.sseClient
            .stream("/api/entities/sse")
            .pipe(
                filter(isEntityEvent),
                map(parseEntityEvent),
                catchError(() => EMPTY),
                takeUntilDestroyed(),
            )
            .subscribe(this.entities$);
    }

    /**
     * Clean up resources when the service is destroyed.
     */
    ngOnDestroy(): void {
        this.entities$.complete();
    }

    /**
     * Create a new entity or update an existing one.
     *
     * @param entity The entity to create or update.
     * @returns An observable that emits the created or updated entity.
     */
    createOrUpdate(entity: Entity): Observable<Entity> {
        return this.httpClient.put<Entity>(`/api/entities/`, entity);
    }

    /**
     * Deletes an entity by its GUID.
     *
     * @param guid The unique identifier of the entity to delete.
     * @returns An observable that completes when the entity is deleted.
     */
    delete(guid: string): Observable<void> {
        return this.httpClient.delete<void>(`/api/entities/${guid}`);
    }

    /**
     * Fetch all entities from the API.
     *
     * @param params Optional query parameters for filtering and pagination.
     * @returns An observable that emits the list of entities.
     */
    findAll(params: FindAllQueryParams = {}): Observable<PaginatedResponse<Entity>> {
        return this.httpClient.get<PaginatedResponse<Entity>>("/api/entities/", {
            params: filterParams(params),
        });
    }

    /**
     * Fetch a specific entity by its GUID.
     *
     * @param guid The unique identifier of the entity.
     * @returns An observable that emits the entity data.
     */
    findOne(guid: string): Observable<Entity> {
        return this.httpClient.get<Entity>(`/api/entities/${guid}`);
    }
}
