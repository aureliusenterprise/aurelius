import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import {
  AppSearchResult,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { IntersectionObserverService } from '@models4insight/services/intersection-observer';
import { Observable } from 'rxjs';
import { switchMapTo } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../services/app-search-results/entity-search-results.service';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../../services/element-search/app-search-document-provider';
import { AppSearchResultService } from '../../../services/element-search/app-search-result.service';
import { ElementSearchService } from '../../../services/element-search/element-search.service';
import { EntitySearchService } from '../../../services/search/entity-search.service';
import { SearchService } from '../../../services/search/search.service';

@Component({
  selector: 'models4insight-classification-source',
  templateUrl: 'classification-source.component.html',
  styleUrls: ['classification-source.component.scss'],
  providers: [
    { provide: SearchService, useClass: EntitySearchService },
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    ElementSearchService,
    AppSearchResultService,
    {
      provide: $APP_SEARCH_DOCUMENT_PROVIDER,
      useExisting: AppSearchResultService,
    },
    IntersectionObserverService,
  ],
})
export class ClassificationSourceComponent {
  readonly isLoading$: Observable<boolean>;
  readonly searchResult$: Observable<AppSearchResult<AtlasEntitySearchObject>>;

  constructor(
    private readonly intersectionObserver: IntersectionObserverService,
    private readonly elementSearchService: ElementSearchService<AtlasEntitySearchObject>,
    private readonly searchResultService: AppSearchResultService<AtlasEntitySearchObject>,
    private readonly router: Router
  ) {
    this.isLoading$ = this.searchResultService.isLoading$;
    this.searchResult$ = this.intersectionObserver.onIntersection.pipe(
      switchMapTo(this.searchResultService.document$)
    );
  }

  openDetails(guid: string) {
    this.router.navigate(['search/details', guid]);
  }

  @Input() set source(source: string) {
    this.elementSearchService.guid = source;
  }
}
