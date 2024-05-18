import { Component, OnInit, ViewChild } from '@angular/core';
import { ModelService } from '@models4insight/services/model';
import { defaultIfFalsy } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';
import { LineageModelComponent } from '../components/lineage-model/lineage-model.component';
import { LineageModelService } from '../components/lineage-model/lineage-model.service';

@Component({
  selector: 'models4insight-process-details',
  templateUrl: 'process-details.component.html',
  styleUrls: ['process-details.component.scss']
})
export class ProcessDetailsComponent implements OnInit {
  hasLineageModel$: Observable<boolean>;
  inputCount$: Observable<number>;
  isLoadingLineageModel$: Observable<boolean>;
  outputCount$: Observable<number>;
  propertyCount$: Observable<number>;
  systemCount$: Observable<number>;

  @ViewChild(LineageModelComponent, { read: LineageModelService, static: true })
  private readonly lineageModelService: LineageModelService;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly filteredPropertiesService: FilteredPropertiesService,
    private readonly modelService: ModelService
  ) {}

  ngOnInit() {
    this.hasLineageModel$ = this.modelService
      .select('model', { includeFalsy: true })
      .pipe(map(Boolean));

    this.inputCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'inputs',
      'length'
    ]);

    this.isLoadingLineageModel$ = this.lineageModelService.select(
      'isRetrievingLineageModel'
    );

    this.outputCount$ = this.entityDetailsService.select([
      'entityDetails',
      'entity',
      'relationshipAttributes',
      'outputs',
      'length'
    ]);

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map(properties => Object.keys(properties).length)
    );

    this.systemCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'system',
          'length'
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));
  }
}
