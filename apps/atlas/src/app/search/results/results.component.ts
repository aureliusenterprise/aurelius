import { Component } from '@angular/core';
import {
  AppSearchResult,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { SHOW_DATA_QUALITY } from '../components/cards/config';
import { AppSearchResultsService } from '../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../services/app-search-results/entity-search-results.service';
import { FilterService } from '../services/filter/filter.service';
import { ResultsFilterService } from './results-filter.service';

@Component({
  selector: 'models4insight-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss'],
  providers: [
    ResultsFilterService,
    { provide: FilterService, useExisting: ResultsFilterService },
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    { provide: SHOW_DATA_QUALITY, useValue: false },
  ],
})
export class ResultsComponent {
  readonly data$: Observable<AppSearchResult<AtlasEntitySearchObject>[]>;
  readonly totalResults$: Observable<number>;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<AtlasEntitySearchObject>
  ) {
    this.data$ = this.searchResultsService.results$;
    this.totalResults$ = this.searchResultsService.totalResults$;
  }

  trackByGuid(
    _: number,
    searchResult: AppSearchResult<AtlasEntitySearchObject>
  ) {
    return searchResult.guid.raw;
  }
}
