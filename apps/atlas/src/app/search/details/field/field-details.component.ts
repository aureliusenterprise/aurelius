import { Component, Inject } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { defaultIfFalsy } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider,
} from '../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';

@Component({
  selector: 'models4insight-field-details',
  templateUrl: 'field-details.component.html',
  styleUrls: ['field-details.component.scss'],
})
export class FieldDetailsComponent {
  readonly attributeCount$: Observable<number>;
  readonly childFieldCount$: Observable<number>;
  readonly dataQualityCount$: Observable<number>;
  readonly dataQualityRulesCount$: Observable<number>;
  readonly dataQualityScore$: Observable<number>;
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
      map((document) => document.dqscorecnt_overall?.raw),
      defaultIfFalsy(0)
    );

    this.attributeCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'attributes',
      'length',
    ]);

    this.childFieldCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'childField',
      'length',
    ]);

    this.dataQualityRulesCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'dataQuality',
      'length',
    ]);

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );
  }
}
