import { Component, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faEdit } from '@fortawesome/free-solid-svg-icons';
import {
  AtlasEntitySearchObject,
  EntityElementWithEXTInfo
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../services/app-search-results/entity-search-results.service';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../services/element-search/app-search-document-provider';
import { AppSearchResultService } from '../services/element-search/app-search-result.service';
import { ElementSearchService } from '../services/element-search/element-search.service';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../services/filtered-properties/filtered-properties.service';
import { EntitySearchService } from '../services/search/entity-search.service';
import { SearchService } from '../services/search/search.service';
import { AttributeDetailsComponent } from './attribute/attribute-details.component';
import { CollectionDetailsComponent } from './collection/collection-details.component';
import { DatasetDetailsComponent } from './dataset/dataset-details.component';
import { DefaultDetailsComponent } from './default/default-details.component';
import { DomainDetailsComponent } from './domain/domain-details.component';
import { EntityDetailsComponent } from './entity/entity-details.component';
import { FieldDetailsComponent } from './field/field-details.component';
import { GovQualityDetailsComponent } from './gov-quality/gov-quality-details.component';
import { PersonDetailsComponent } from './person/person-details.component';
import { ProcessDetailsComponent } from './process/process-details.component';
import { SystemDetailsComponent } from './system/system-details.component';

const componentsByType = {
  m4i_data_domain: DomainDetailsComponent,
  m4i_data_entity: EntityDetailsComponent,
  m4i_data_attribute: AttributeDetailsComponent,
  m4i_field: FieldDetailsComponent,
  m4i_dataset: DatasetDetailsComponent,
  m4i_collection: CollectionDetailsComponent,
  m4i_system: SystemDetailsComponent,
  m4i_person: PersonDetailsComponent,
  m4i_generic_process: ProcessDetailsComponent,
  m4i_gov_data_quality: GovQualityDetailsComponent,
};

@Component({
  selector: 'models4insight-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.scss'],
  providers: [
    EntityDetailsService,
    FilteredPropertiesService,
    { provide: SearchService, useClass: EntitySearchService },
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    ElementSearchService,
    AppSearchResultService,
    {
      provide: $APP_SEARCH_DOCUMENT_PROVIDER,
      useExisting: AppSearchResultService,
    },
  ],
})
export class DetailsComponent implements OnDestroy {
  readonly faEdit = faEdit;

  readonly detailsComponent$: Observable<typeof Component>;
  readonly entityDetails$: Observable<EntityElementWithEXTInfo>;
  readonly isRetrievingDetails$: Observable<boolean>;

  constructor(
    private readonly router: Router,
    private readonly activatedRoute: ActivatedRoute,
    private readonly entityDetailsService: EntityDetailsService,
    private readonly elementSearchService: ElementSearchService<AtlasEntitySearchObject>
  ) {
    this.activatedRoute.data
      .pipe(
        map((data) => data.entityId),
        untilDestroyed(this)
      )
      .subscribe((entityId) => {
        this.entityDetailsService.entityId = entityId;
        this.elementSearchService.guid = entityId;
      });

    this.detailsComponent$ = this.entityDetailsService.entityDetails$.pipe(
      map(
        (entity) => componentsByType[entity.typeName] ?? DefaultDetailsComponent
      )
    );

    this.entityDetails$ = this.entityDetailsService.entityDetails$;

    this.isRetrievingDetails$ = this.entityDetailsService.select(
      'isRetrievingDetails'
    );
  }

  ngOnDestroy() {}

  navigateToEditEntity(guid: string) {
    this.router.navigate(['/search/edit-entity', guid]);
  }
}
