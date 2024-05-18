import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { ModelService } from '@models4insight/services/model';
import { defaultIfFalsy } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider,
} from '../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';
import { LineageModelComponent } from '../components/lineage-model/lineage-model.component';
import { LineageModelService } from '../components/lineage-model/lineage-model.service';

@Component({
  selector: 'models4insight-dataset-details',
  templateUrl: 'dataset-details.component.html',
  styleUrls: ['dataset-details.component.scss'],
})
export class DatasetDetailsComponent implements OnInit {
  readonly childDatasetCount$: Observable<number>;
  readonly consumerCount$: Observable<number>;
  readonly dataQualityCount$: Observable<number>;
  readonly dataQualityScore$: Observable<number>;
  readonly entityCount$: Observable<number>;
  readonly fieldCount$: Observable<number>;
  readonly hasLineageModel$: Observable<boolean>;
  readonly producerCount$: Observable<number>;
  readonly propertyCount$: Observable<number>;

  isLoadingLineageModel$: Observable<boolean>;

  @ViewChild(LineageModelComponent, { read: LineageModelService, static: true })
  private readonly lineageModelService: LineageModelService;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly filteredPropertiesService: FilteredPropertiesService,
    private readonly modelService: ModelService,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    this.childDatasetCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'childDataset',
      'length',
    ]);

    this.consumerCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'inputToProcesses',
      'length',
    ]);

    this.dataQualityCount$ = this.searchResultService.document$.pipe(
      map((document) => document.dqscorecnt_overall?.raw),
      defaultIfFalsy(0)
    );

    this.dataQualityScore$ = this.searchResultService.document$.pipe(
      map((document) => document.dqscore_overall?.raw),
      defaultIfFalsy(0)
    );

    this.entityCount$ = this.searchResultService.document$.pipe(
      map((document) => document.deriveddataentity?.raw?.length),
      defaultIfFalsy(0)
    );

    this.fieldCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'fields',
      'length',
    ]);

    this.hasLineageModel$ = this.modelService
      .select('model', { includeFalsy: true })
      .pipe(map(Boolean));

    this.producerCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'outputFromProcesses',
      'length',
    ]);

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );
  }

  ngOnInit(): void {
    this.isLoadingLineageModel$ = this.lineageModelService.select(
      'isRetrievingLineageModel'
    );
  }
}
