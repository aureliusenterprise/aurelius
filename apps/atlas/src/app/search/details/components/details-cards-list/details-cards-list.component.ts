import { Component, Input, OnDestroy, Optional } from '@angular/core';
import {
  faArrowAltCircleDown,
  faFilter,
} from '@fortawesome/free-solid-svg-icons';
import {
  AppSearchDocument,
  AppSearchResult,
  ElasticSearchResult,
} from '@models4insight/atlas/api';
import {
  defaultSimpleSearchInputContext,
  SimpleSearchInputContext,
} from '@models4insight/components';
import { combineLatest, Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { v4 as uuid4 } from 'uuid';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { FilterService } from '../../../services/filter/filter.service';
import { DetailsCardsSearchService } from './services/details-cards-search.service';
import { ShowDescendantsService } from './show-descendants-control.directive';

const searchBarContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  label: null,
  placeholder: 'Search for an entity',
};

@Component({
  selector: 'models4insight-details-cards-list',
  templateUrl: 'details-cards-list.component.html',
  styleUrls: ['details-cards-list.component.scss'],
  providers: [FilterService],
})
export class DetailsCardsListComponent<
  T extends AppSearchDocument = AppSearchDocument
> implements OnDestroy
{
  readonly arrowDown = faArrowAltCircleDown;
  readonly descendantsControlId = uuid4();
  readonly faFilter = faFilter;
  readonly searchBarContext = searchBarContext;

  readonly showAllDescendants$: Observable<boolean>;

  readonly entities$: Observable<AppSearchResult<T>[]>;
  readonly isFilterActive$: Observable<boolean>;
  readonly isLoadingResults$: Observable<boolean>;
  readonly totalResults$: Observable<number>;
  readonly query$: Observable<string>;

  @Input() enableDescendantsControl = true;
  @Input() sortingOptions: string[] = [];
  @Input() title: string;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<T>,
    private readonly searchService: DetailsCardsSearchService<T>,
    @Optional() private readonly showDescendantsService: ShowDescendantsService
  ) {
    this.entities$ = this.searchResultsService.results$;
    this.showAllDescendants$ = this.showDescendantsService?.showDescendants$;

    this.isFilterActive$ = combineLatest([
      this.searchService.isFilterActive$,
      this.showAllDescendants$ ?? of(false),
    ]).pipe(
      map(
        ([isFilterActive, showAllDescendants]) =>
          isFilterActive || showAllDescendants
      )
    );

    this.isLoadingResults$ = this.searchResultsService.isLoadingPage$;
    this.totalResults$ = this.searchResultsService.totalResults$;
    this.query$ = this.searchService.queryObject$.pipe(
      map((queryObject) => queryObject.query)
    );
  }

  ngOnDestroy() {}

  reset() {
    this.showDescendantsService?.reset();
    this.searchService.reset();
  }

  protected trackByGuid(_: number, searchResult: ElasticSearchResult) {
    return searchResult.guid?.raw;
  }

  set query(query: string) {
    this.searchService.query = query;
  }
}
