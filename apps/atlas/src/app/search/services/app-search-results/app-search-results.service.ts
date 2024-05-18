import { Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchPage,
  AppSearchQuery,
  AppSearchResult,
  AppSearchResults,
  AppSearchResultsFacets,
  AppSearchService,
  Meta,
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { combineLatest, Observable, Subject } from 'rxjs';
import {
  filter,
  map,
  scan,
  shareReplay,
  startWith,
  switchMap,
  tap,
  withLatestFrom,
} from 'rxjs/operators';
import { SearchService } from '../search/search.service';

export interface AppSearchResultsStoreContext {
  readonly isLoadingPage?: boolean;
  readonly pageSize?: number;
}

@Injectable()
export class AppSearchResultsService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> extends BasicStore<AppSearchResultsStoreContext> {
  /**
   * An observable stream of whether or not a page is currently being loaded.
   */
  readonly isLoadingPage$: Observable<boolean>;

  /**
   * An observable stream of the current maximum size of a page.
   */
  readonly pageSize$: Observable<number>;

  /**
   * An observable stream of the first page of search results.
   */
  readonly firstPage$: Observable<AppSearchResults<T, P>>;

  /**
   * An observable stream of the facets associated with the first page.
   */
  readonly facets$: Observable<AppSearchResultsFacets<T>>;

  /**
   * An observable stream of the metadata associated with the first page.
   */
  readonly meta$: Observable<Meta>;

  /**
   * An observable stream of the total number of results for the current query.
   */
  readonly totalResults$: Observable<number>;

  /**
   * An observable stream of all pages loaded so far.
   */
  readonly results$: Observable<AppSearchResult<P>[]>;

  /**
   * An observable stream that automatically loads all pages when subscribed to.
   */
  readonly allResults$: Observable<AppSearchResult<P>[]>;

  /**
   * An observable stream of whether or not all results have been loaded.
   */
  readonly allResultsLoaded$: Observable<boolean>;

  /**
   * Triggers the loading of the next page of search results.
   */
  private readonly nextPage$: Subject<void>;

  constructor(
    private readonly appSearchService: AppSearchService<T, P>,
    private readonly searchService: SearchService<T, P>
  ) {
    super({ defaultState: { isLoadingPage: false, pageSize: 10 } });

    this.isLoadingPage$ = this.select('isLoadingPage');
    this.pageSize$ = this.select('pageSize');

    this.firstPage$ = combineLatest([
      this.searchService.queryObject$,
      this.pageSize$,
    ]).pipe(
      switchMap(([queryObject, pageSize]) =>
        this.getFirstPage(queryObject, pageSize)
      ),
      shareReplay({ refCount: true })
    );

    this.facets$ = this.firstPage$.pipe(
      map((searchContext) => searchContext.facets)
    );

    this.meta$ = this.firstPage$.pipe(
      map((searchContext) => searchContext.meta)
    );

    this.totalResults$ = this.meta$.pipe(
      map((meta) => meta.page.total_results)
    );

    this.nextPage$ = new Subject();

    const currentIndex$ = this.meta$.pipe(
      switchMap((meta) =>
        this.nextPage$.pipe(
          scan((currentPage) => currentPage + 1, 1),
          filter((currentPage) => currentPage <= meta.page.total_pages)
        )
      )
    );

    const currentPage$ = currentIndex$.pipe(
      withLatestFrom(this.searchService.queryObject$, this.pageSize$),
      switchMap(([currentPage, queryObject, pageSize]) =>
        this.getPage(currentPage, queryObject, pageSize)
      )
    );

    this.results$ = this.firstPage$.pipe(
      switchMap((context) =>
        currentPage$.pipe(
          startWith(context),
          scan((documents, page) => [...documents, ...page.results], [])
        )
      ),
      shareReplay({ refCount: true })
    );

    this.allResults$ = this.results$.pipe(tap(() => this.nextPage()));

    this.allResultsLoaded$ = combineLatest([this.results$, this.meta$]).pipe(
      map(([results, meta]) => results.length === meta.page.total_results)
    );
  }

  /**
   * Triggers loading the next page of search results
   */
  nextPage() {
    this.nextPage$.next();
  }

  private getFirstPage(queryObject: AppSearchQuery<T, P>, pageSize: number) {
    return this.getPage(1, queryObject, pageSize);
  }

  @ManagedTask('Loading a page of search results', { isQuiet: true })
  @MonitorAsync('isLoadingPage')
  private async getPage(
    currentPage: number,
    queryObject: AppSearchQuery<T, P>,
    pageSize: number
  ) {
    const page: AppSearchPage = {
      current: currentPage,
      size: pageSize,
    };

    queryObject = {
      ...queryObject,
      page,
    };

    return this.appSearchService.search(queryObject).toPromise();
  }

  set pageSize(pageSize: number) {
    this.update({
      description: 'New page size available',
      payload: { pageSize },
    });
  }
}
