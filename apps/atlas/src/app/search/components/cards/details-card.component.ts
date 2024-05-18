import {
  Component,
  EventEmitter,
  Inject,
  Input,
  OnDestroy,
  Optional,
  Output,
} from '@angular/core';
import { Router } from '@angular/router';
import {
  AppSearchDocument,
  AppSearchResult,
  EntityElementWithEXTInfo,
} from '@models4insight/atlas/api';
import { IntersectionObserverService } from '@models4insight/services/intersection-observer';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { map, switchMapTo } from 'rxjs/operators';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../services/element-search/app-search-document-provider';
import { AppSearchDocumentService } from '../../services/element-search/app-search-document.service';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { AttributeDetailsCardComponent } from './attribute/attribute-details-card.component';
import { CollectionDetailsCardComponent } from './collection/collection-details-card.component';
import { SHOW_GOV_QUALITY } from './config';
import { DataQualityCardComponent } from './data-quality/data-quality-card.component';
import { DatasetDetailsCardComponent } from './dataset/dataset-details-card.component';
import { DomainDetailsCardComponent } from './domain/domain-details-card.component';
import { EntityDetailsCardComponent } from './entity/entity-details-card.component';
import { FieldDetailsCardComponent } from './field/field-details-card.component';
import { GovernanceQualityCardComponent } from './gov-quality/governance-quality-card.component';
import { SystemDetailsCardComponent } from './system/system-details-card.component';

const cardsByType: Dictionary<any> = {
  m4i_data_domain: DomainDetailsCardComponent,
  m4i_data_entity: EntityDetailsCardComponent,
  m4i_data_attribute: AttributeDetailsCardComponent,
  m4i_field: FieldDetailsCardComponent,
  m4i_dataset: DatasetDetailsCardComponent,
  m4i_collection: CollectionDetailsCardComponent,
  m4i_system: SystemDetailsCardComponent,
  m4i_data_quality: DataQualityCardComponent,
  m4i_gov_data_quality: GovernanceQualityCardComponent,
};

@Component({
  selector: 'models4insight-details-card',
  templateUrl: 'details-card.component.html',
  styleUrls: ['details-card.component.scss'],
  providers: [
    EntityDetailsService,
    IntersectionObserverService,
    AppSearchDocumentService,
    {
      provide: $APP_SEARCH_DOCUMENT_PROVIDER,
      useExisting: AppSearchDocumentService,
    },
  ],
})
export class DetailsCardComponent implements OnDestroy {
  /**
   * An observable stream of the current details card template based on the current entity type.
   */
  readonly cardComponent$: Observable<typeof Component>;

  /**
   * An observable stream of the current Atlas entity.
   */
  readonly entity$: Observable<EntityElementWithEXTInfo>;

  /**
   * An observable stream indicating whether or not entity details are currently being loaded from the API.
   */
  readonly isRetrievingDetails$: Observable<boolean>;

  /**
   * An observable stream of the name of the current entity.
   */
  readonly name$: Observable<string>;

  /**
   * The details card templates mapped to their respective base types.
   */
  readonly cardsByType: Dictionary<typeof Component> = cardsByType;

  /**
   * Whether or not to show the governance quality indicator at the bottom right of the card.
   */
  readonly showGovQuality: boolean;

  /**
   * Emits an event whenever the card title is clicked.
   */
  @Output() entityClicked = new EventEmitter<string>();

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly intersectionObserver: IntersectionObserverService,
    private readonly router: Router,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentService<AppSearchDocument>,
    @Optional() @Inject(SHOW_GOV_QUALITY) showGovQuality: boolean
  ) {
    this.showGovQuality = showGovQuality ?? true;

    this.cardComponent$ = this.entityDetailsService.entityDetails$.pipe(
      map((entity) => cardsByType[entity.typeName])
    );

    this.entity$ = this.entityDetailsService.entityDetails$;

    this.isRetrievingDetails$ = this.entityDetailsService.select(
      'isRetrievingDetails'
    );

    this.name$ = this.searchResultService.document$.pipe(
      map((document) => document.name?.raw)
    );

    this.intersectionObserver.onIntersection
      .pipe(
        switchMapTo(this.searchResultService.document$),
        untilDestroyed(this)
      )
      .subscribe(
        (document) => (this.entityDetailsService.entityId = document.guid?.raw)
      );
  }

  ngOnDestroy() {}

  /**
   * Navigates to the details page of the entity with the given `guid`.
   */
  protected openDetails(guid: string) {
    this.router.navigate(['search/details', guid]);
  }

  /**
   * Handles clicks on the card title.
   * @param guid The unique id of the current entity.
   */
  protected onEntityClick(guid: string) {
    if (this.entityClicked.observers.length > 0) {
      this.entityClicked.emit(guid);
    } else {
      this.openDetails(guid);
    }
  }

  /**
   * Updates the current base card data.
   */
  @Input() set searchResult(searchResult: AppSearchResult<AppSearchDocument>) {
    this.searchResultService.document = searchResult;
  }
}
