import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  compareModels,
  ModelCompareDifference,
  ModelCompareDifferenceType
} from '@models4insight/repository';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Subject } from 'rxjs';
import { exhaustMap, switchMap } from 'rxjs/operators';

export interface CompareModelsStoreContext {
  readonly differences?: ModelCompareDifference[];
  readonly differencePerConceptId?: Dictionary<ModelCompareDifferenceType>;
  readonly isComparingModels?: boolean;
  readonly isCreatingDifferenceMapping?: boolean;
}

export const defaultCompareModelsServiceState: CompareModelsStoreContext = {
  isComparingModels: false,
  isCreatingDifferenceMapping: false
};

@Injectable()
export class ModelCompareService extends BasicStore<CompareModelsStoreContext> {
  private readonly compareModels$ = new Subject<
    [string, string, number?, number?]
  >();

  constructor(
    private readonly modelService: ModelService,
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultCompareModelsServiceState,
      name: 'CompareModelsService',
      storeService
    });
    this.init();
  }

  private init() {
    this.compareModels$
      .pipe(
        exhaustMap(
          ([baseBranchName, otherBranchName, baseVersion, otherVersion]) =>
            this.handleCompareModels(
              baseBranchName,
              otherBranchName,
              baseVersion,
              otherVersion
            )
        ),
        untilDestroyed(this)
      )
      .subscribe();

    this.select('differences')
      .pipe(
        switchMap(differences =>
          this.handleCreateDifferenceMapping(differences)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  compareModels(
    baseBranchName: string,
    otherBranchName: string,
    baseVersion?: number,
    otherVersion?: number
  ) {
    this.compareModels$.next([
      baseBranchName,
      otherBranchName,
      baseVersion,
      otherVersion
    ]);
  }

  @ManagedTask('Comparing the models', { isQuiet: true })
  @MonitorAsync('isComparingModels')
  private async handleCompareModels(
    baseBranchName: string,
    otherBranchName: string,
    baseVersion?: number,
    otherVersion?: number
  ) {
    const { project } = await this.projectService.getCurrentProject();

    const { model, differences } = await compareModels(
      project,
      baseBranchName,
      otherBranchName,
      { baseVersion, otherVersion }
    ).toPromise();

    this.modelService.model = model;

    this.update({
      description: 'New differences available',
      payload: { differences }
    });
  }

  @ManagedTask('Preparing the model differences', { isQuiet: true })
  @MonitorAsync('isCreatingDifferenceMapping')
  private async handleCreateDifferenceMapping(
    differences: ModelCompareDifference[]
  ) {
    const differencePerConceptId: Dictionary<ModelCompareDifferenceType> = {};

    // Filter out unchanged differences
    for (const { id, difference } of differences) {
      if (difference !== 'unchanged') {
        differencePerConceptId[id] = difference;
      }
    }

    this.update({
      description: 'New difference mapping available',
      payload: { differencePerConceptId }
    });
  }
}
