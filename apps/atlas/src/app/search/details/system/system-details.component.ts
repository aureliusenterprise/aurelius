import { Component, Inject } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { $APP_SEARCH_DOCUMENT_PROVIDER, AppSearchDocumentProvider } from '../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';

@Component({
  selector: 'models4insight-system-details',
  templateUrl: 'system-details.component.html',
  styleUrls: ['system-details.component.scss'],
})
export class SystemDetailsComponent {
  readonly collectionCount$: Observable<number>;
  readonly dataQualityScore$: Observable<number>;
  readonly dataQualityCount$: Observable<number>;
  readonly propertyCount$: Observable<number>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly filteredPropertiesService: FilteredPropertiesService,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    this.dataQualityScore$ = this.searchResultService.document$.pipe(
      map((document) => document.dqscore_overall?.raw)
    );

    this.dataQualityCount$ = this.searchResultService.document$.pipe(
      map((document) => document.dqscorecnt_overall?.raw)
    );

    this.collectionCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'collections',
      'length',
    ]);

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );
  }
}
