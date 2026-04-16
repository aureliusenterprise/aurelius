import { computed, inject, Injectable, InjectionToken, Signal, signal } from "@angular/core";
import { takeUntilDestroyed, toObservable, toSignal } from "@angular/core/rxjs-interop";
import { EntitiesService, Entity, FindAllQueryParams, PaginatedResponse } from "aurelius-data-access";
import { catchError, debounceTime, EMPTY, finalize, merge, Observable, Subject, switchMap, tap } from "rxjs";

export const SEARCH_SERVICE_DEBOUNCE_MS = new InjectionToken<number>("SEARCH_SERVICE_DEBOUNCE_MS", {
    providedIn: "root",
    factory: () => 300,
});

@Injectable({
    providedIn: "root",
})
export class SearchService {
    /**
     * The current list of entities based on the search query.
     */
    readonly entities: Signal<PaginatedResponse<Entity>>;

    /**
     * The latest error encountered during the search operation.
     */
    readonly error = signal<Error | null>(null);

    /**
     * The loading state of the search service.
     */
    readonly loading = signal<boolean>(false);

    /**
     * The current page index for pagination.
     */
    readonly pageIndex = signal<number>(0);

    /**
     * The number of entities to display per page.
     */
    readonly pageSize = signal<number>(6);

    /**
     * The current search query.
     */
    readonly query = signal<string>("");

    /**
     * The debounce delay for search queries in milliseconds.
     */
    private readonly debounceMillis = inject<number>(SEARCH_SERVICE_DEBOUNCE_MS);

    /**
     * The API client for making HTTP requests.
     */
    private readonly entitiesService = inject(EntitiesService);

    /**
     * A subject used to trigger a refresh of the entities list.
     */
    private readonly refresh$ = new Subject<void>();

    /**
     * The search parameters computed from the current query, page index, and page size.
     */
    private readonly searchParams = computed(() => this.buildSearchParams());

    constructor() {
        /**
         * Whenever the search parameters change or a refresh is triggered, perform a search for entities.
         * The search results are debounced to avoid excessive API calls.
         * The loading state is updated accordingly to provide feedback to the user.
         */
        const entities$ = merge(this.refresh$, toObservable(this.searchParams)).pipe(
            debounceTime(this.debounceMillis),
            tap(() => this.startSearch()),
            switchMap(() =>
                this.entitiesService.findAll(this.searchParams()).pipe(
                    catchError((err) => this.handleError(err)),
                    finalize(() => this.loading.set(false)),
                ),
            ),
        );

        /**
         * Convert the entities observable to a signal for use in the UI.
         */
        this.entities = toSignal(entities$, { initialValue: { total: 0, data: [] } });

        /**
         * Refresh the search results whenever an entity is created, updated, or deleted.
         */
        this.entitiesService.entities$.pipe(takeUntilDestroyed()).subscribe(() => this.refresh());
    }

    /**
     * Trigger a refresh of the entities list.
     */
    refresh(): void {
        this.refresh$.next();
    }

    /**
     * Build the search parameters for the API request based on the current query, page index, and page size.
     * @returns The search parameters.
     */
    private buildSearchParams(): FindAllQueryParams {
        return {
            search: this.query(),
            skip: this.pageIndex() * this.pageSize(),
            limit: this.pageSize(),
        };
    }

    /**
     * Handle errors that occur during the search operation.
     * @param error The error that occurred.
     * @returns An empty observable to complete the stream.
     */
    private handleError(error: Error): Observable<never> {
        this.error.set(error);
        return EMPTY;
    }

    /**
     * Start the search operation by setting the loading state and clearing any previous errors.
     */
    private startSearch(): void {
        this.loading.set(true);
        this.error.set(null);
    }
}
