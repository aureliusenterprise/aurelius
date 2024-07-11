import { Component, OnDestroy } from '@angular/core';
import {
  AtlasEntitySearchObject,
  ElasticSearchResult
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { ModelExplorerService } from 'libs/modelview2/src/lib/model-explorer.service';
import { ModelElement } from 'libs/modelview2/src/lib/parsers';
import { combineLatest, Observable } from 'rxjs';
import { filter, map, switchMap } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../../services/app-search-results/entity-search-results.service';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../../../services/element-search/app-search-document-provider';
import { AppSearchResultService } from '../../../../services/element-search/app-search-result.service';
import { ElementSearchService } from '../../../../services/element-search/element-search.service';
import { SearchService } from '../../../../services/search/search.service';

@Component({
  selector: 'models4insight-model-explorer-data-governance',
  templateUrl: 'model-explorer-data-governance.component.html',
  styleUrls: ['model-explorer-data-governance.component.scss'],
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    ElementSearchService,
  ],
})
export class ModelExplorerDataGovernanceComponent implements OnDestroy {
  readonly isLoading$: Observable<boolean>;
  readonly searchResult$: Observable<ElasticSearchResult>;
  readonly showDetailsCard$: Observable<boolean>;

  constructor(
    private readonly elementSearchService: ElementSearchService<AtlasEntitySearchObject>,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly searchResultService: AppSearchResultService<AtlasEntitySearchObject>
  ) {
    this.isLoading$ = this.searchResultService.isLoading$;
    this.searchResult$ = this.searchResultService.document$;

    this.showDetailsCard$ = combineLatest([
      this.modelExplorerService.select('selectedEntity'),
      this.searchResultService.document$,
    ]).pipe(
      map(
        ([selectionId, searchResult]) => selectionId === searchResult.guid?.raw
      )
    );

    this.modelExplorerService
      .select('selectedEntity')
      .pipe(
        switchMap((selectionId) =>
          this.modelExplorerService.select(['elements', selectionId], {
            includeFalsy: true,
          })
        ),
        filter(Boolean),
        untilDestroyed(this)
      )
      .subscribe((selectedElement: ModelElement) => {
        this.elementSearchService.guid = selectedElement.id;
      });
  }

  ngOnDestroy() {}
}
