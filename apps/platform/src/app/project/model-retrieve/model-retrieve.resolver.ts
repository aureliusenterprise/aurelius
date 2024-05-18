import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  Resolve,
  RouterStateSnapshot
} from '@angular/router';
import {
  BranchSummary,
  getBranchesSummary,
  getProvenance,
  ModelProvenance
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { FilterContext, ModelRetrieveService } from './model-retrieve.service';

export interface ModelRetrieveParams {
  branches: BranchSummary[];
  filter: FilterContext;
  models: ModelProvenance[];
}

export const MODEL_RETRIEVE_BATCH_SIZE = 20;
export const MODEL_RETRIEVE_DEFAULT_PAGE_INDEX = 1;

@Injectable()
export class ModelRetrieveResolver implements Resolve<ModelRetrieveParams> {
  constructor(
    private readonly projectService: ProjectService,
    private readonly modelRetrieveService: ModelRetrieveService
  ) {}

  async resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<ModelRetrieveParams> {
    const { project } = await this.projectService.getCurrentProject();

    const filter: FilterContext = {
      pageIndex:
        Number.parseInt(route.queryParamMap.get('modelsPageIndex'), 10) ||
        MODEL_RETRIEVE_DEFAULT_PAGE_INDEX,
      branch: route.queryParamMap.get('branch'),
      from: Number.parseInt(route.queryParamMap.get('from'), 10) || undefined,
      latestOnly: route.queryParamMap.get('latestOnly') === 'true',
      search: route.queryParamMap.get('search'),
      until: Number.parseInt(route.queryParamMap.get('to'), 10) || undefined
    };

    const [branches, models] = await Promise.all([
      this.handleGetBranchesSummary(project, filter),
      this.handleGetProvenance(project, filter)
    ]);

    const result = { branches, filter, models };

    this.modelRetrieveService.update({
      description: 'New model retrieve data available',
      payload: result
    });

    return result;
  }

  @ManagedTask('Retrieving the model versions', { isQuiet: true })
  private handleGetProvenance(projectName: string, filter: FilterContext) {
    return getProvenance(projectName, {
      batchSize: MODEL_RETRIEVE_BATCH_SIZE,
      offset: (filter.pageIndex - 1) * MODEL_RETRIEVE_BATCH_SIZE,
      queryString: filter.search,
      branchName: filter.branch,
      latestOnly: filter.latestOnly,
      from: filter.from,
      until: filter.until,
      forceUpdate: true
    }).toPromise();
  }

  @ManagedTask('Retrieving statistics for the project branches', {
    isQuiet: true
  })
  private handleGetBranchesSummary(projectName: string, filter: FilterContext) {
    return getBranchesSummary(projectName, {
      queryString: filter.search,
      branchName: filter.branch,
      latestOnly: filter.latestOnly,
      from: filter.from,
      until: filter.until,
      forceUpdate: true
    }).toPromise();
  }
}
