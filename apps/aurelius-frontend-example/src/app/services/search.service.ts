import { inject, Injectable, Signal, signal } from "@angular/core";
import { toObservable, toSignal } from "@angular/core/rxjs-interop";
import { EntitiesService, Entity } from "aurelius-data-access";
import { catchError, debounceTime, EMPTY, finalize, merge, Observable, Subject, switchMap, tap } from "rxjs";

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
     * The API client for making HTTP requests.
     */
    private readonly entitiesService = inject(EntitiesService);

    /**
     * A subject used to trigger a refresh of the entities list.
     */
    private readonly refresh$ = new Subject<void>();

    constructor() {
        const entities$ = merge(this.refresh$, toObservable(this.query)).pipe(
            debounceTime(300),
            tap(() => this.startSearch()),
            switchMap(() =>
                this.entitiesService.findAll({ search: this.query() }).pipe(
                    catchError((err) => this.handleError(err)),
                    finalize(() => this.loading.set(false)),
                ),
            ),
        );
        this.entities = toSignal(entities$, { initialValue: [] });
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
