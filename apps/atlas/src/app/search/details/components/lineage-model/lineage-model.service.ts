import { Injectable } from '@angular/core';
import { getLineageModel } from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ModelDataService, ModelService } from '@models4insight/services/model';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { switchMap } from 'rxjs/operators';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';

export interface LineageModelStoreContext {
  readonly isRetrievingLineageModel?: boolean;
}

@Injectable()
export class LineageModelService extends BasicStore<LineageModelStoreContext> {
  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly modelService: ModelService,
    private readonly modelDataService: ModelDataService
  ) {
    super();
    this.init();
  }

  private init() {
    this.entityDetailsService
      .select('entityId')
      .pipe(
        switchMap(entityId => this.handleRetrieveLineageModel(entityId)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @ManagedTask('Retrieving the lineage model', { isQuiet: true })
  @MonitorAsync('isRetrievingLineageModel')
  private async handleRetrieveLineageModel(guid: string) {
    try {
      const response = await getLineageModel(guid).toPromise();
      this.modelService.model = JSON.parse(response?.model);

      const dataByConceptId = response?.metadata.reduce(
        (result, { id, data }) => ({ ...result, [id]: data }),
        {}
      );

      this.modelDataService.dataByConceptId = dataByConceptId;
    } catch {
      this.modelService.delete({
        description: 'No lineage model available',
        path: ['model']
      });
    }
  }
}
