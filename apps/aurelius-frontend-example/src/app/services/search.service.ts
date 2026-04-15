import { inject, Injectable, InjectionToken, Signal, signal } from "@angular/core";
import { takeUntilDestroyed, toObservable, toSignal } from "@angular/core/rxjs-interop";
import { EntitiesService, Entity } from "aurelius-data-access";
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
    readonly entities: Signal<Entity[]>;

    /**
     * The latest error encountered during the search operation.
     */
    readonly error = signal<Error | null>(null);

    /**
     * The loading state of the search service.
     */
    readonly loading = signal<boolean>(false);

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

    constructor() {
        /**
         * Whenever the search query changes or a refresh is triggered, perform a search for entities matching the query.
         * The search results are debounced to avoid excessive API calls.
         * The loading state is updated accordingly to provide feedback to the user.
         */
        const entities$ = merge(this.refresh$, toObservable(this.query)).pipe(
            debounceTime(this.debounceMillis),
            tap(() => this.startSearch()),
            switchMap(() =>
                this.entitiesService.findAll({ search: this.query() }).pipe(
                    catchError((err) => this.handleError(err)),
                    finalize(() => this.loading.set(false)),
                ),
            ),
        );

        /**
         * Convert the entities observable to a signal for use in the UI.
         */
        this.entities = toSignal(entities$, { initialValue: [] });

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
