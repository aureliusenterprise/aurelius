import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { commitData } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Subject } from 'rxjs';
import { exhaustMap, first } from 'rxjs/operators';
import { ModelDataService } from './model-data.service';
import { ServicesModelModule } from './services-model.module';

function* formatData(dataByConceptId: Dictionary<Dictionary<any>>) {
  for (const [id, data] of Object.entries(dataByConceptId)) {
    yield {
      id,
      data,
    };
  }
}

export interface ModelDataCommitStoreContext {
  readonly isCommittingData?: boolean;
}

@Injectable({
  providedIn: ServicesModelModule,
})
export class ModelDataCommitService extends BasicStore<ModelDataCommitStoreContext> {
  private readonly commitData$ = new Subject<string>();
  private readonly dataCommitted$ = new Subject<string>();

  constructor(
    private readonly modelDataService: ModelDataService,
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({ name: 'ModelDataCommitService', storeService });
    this.init();
  }

  private init() {
    this.commitData$
      .pipe(
        exhaustMap((branch) => this.handleCommitData(branch)),
        untilDestroyed(this)
      )
      .subscribe(this.dataCommitted$);
  }

  async commitData(branch: string) {
    this.commitData$.next(branch);
    return this.onDataCommitted.pipe(first()).toPromise();
  }

  get onDataCommitted() {
    return this.dataCommitted$.asObservable();
  }

  @ManagedTask('Committing the model data')
  @MonitorAsync('isCommittingData')
  private async handleCommitData(branch: string) {
    const [{ project }, data] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.modelDataService.get('dataByConceptId'),
    ]);

    const formattedData = Array.from(formatData(data));

    return commitData(project, branch, formattedData).toPromise();
  }
}
