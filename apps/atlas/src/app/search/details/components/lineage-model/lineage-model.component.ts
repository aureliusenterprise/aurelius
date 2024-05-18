import { Component, OnInit } from '@angular/core';
import { ModelService } from '@models4insight/services/model';
import { MODEL_BROWSER_SELECTION_ADDONS } from 'libs/modelview2/src/lib/model-browser/selection/selection.component';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { LineageModelService } from './lineage-model.service';
import { ModelExplorerDataGovernanceComponent } from './model-explorer-data-governance/model-explorer-data-governance.component';

const addons = {
  'Data governance': ModelExplorerDataGovernanceComponent
};

@Component({
  selector: 'models4insight-lineage-model',
  templateUrl: 'lineage-model.component.html',
  styleUrls: ['lineage-model.component.scss'],
  providers: [
    LineageModelService,
    { provide: MODEL_BROWSER_SELECTION_ADDONS, useValue: addons }
  ]
})
export class LineageModelComponent implements OnInit {
  entityId$: Observable<string>;
  isRetrievingLineageModel$: Observable<boolean>;
  hasLineageModel$: Observable<boolean>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly lineageModelService: LineageModelService,
    private readonly modelService: ModelService
  ) {}

  ngOnInit() {
    this.entityId$ = this.entityDetailsService.select('entityId');

    this.isRetrievingLineageModel$ = this.lineageModelService.select(
      'isRetrievingLineageModel'
    );

    this.hasLineageModel$ = this.modelService
      .select('model', { includeFalsy: true })
      .pipe(map(Boolean));
  }
}
