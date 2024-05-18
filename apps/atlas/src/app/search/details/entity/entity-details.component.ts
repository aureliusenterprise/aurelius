import { Component, Inject } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { defaultIfFalsy } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider
} from '../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';

@Component({
  selector: 'models4insight-entity-details',
  templateUrl: 'entity-details.component.html',
  styleUrls: ['entity-details.component.scss'],
})
export class EntityDetailsComponent {
  readonly attributeCount$: Observable<number>;
  readonly childEntityCount$: Observable<number>;
  readonly dataQualityCount$: Observable<number>;
  readonly dataQualityScore$: Observable<number>;
  readonly datasetCount$: Observable<number>;
  readonly propertyCount$: Observable<number>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly filteredPropertiesService: FilteredPropertiesService,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    this.dataQualityScore$ = this.searchResultService.document$.pipe(
      map((document) => document?.dqscore_overall?.raw)
    );

    this.dataQualityCount$ = this.searchResultService.document$.pipe(
      map((document) => document?.dqscorecnt_overall?.raw)
    );

    this.datasetCount$ = this.searchResultService.document$.pipe(
      map((document) => document?.deriveddataset?.raw?.length),
      defaultIfFalsy(0)
    );

    this.attributeCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'attributes',
      'length',
    ]);

    this.childEntityCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'childEntity',
      'length',
    ]);

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );
  }
}
