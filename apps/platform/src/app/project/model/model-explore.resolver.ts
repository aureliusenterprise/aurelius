import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';
import { ModelService } from '@models4insight/services/model';
import { ModelExploreService } from './model-explore.service';

@Injectable()
export class ModelExploreResolver implements Resolve<void> {
  constructor(
    private readonly modelService: ModelService,
    private readonly modelExploreService: ModelExploreService,
  ) {}

  async resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<void> {
    const branch: string = route.queryParamMap.get('branchName'),
      version = Number.parseInt(route.queryParamMap.get('version'), 10);

    this.modelService.update({
      description: 'New model parameters available',
      payload: { branch, version }
    });

    this.modelExploreService.update({
      description: 'New explorer parameters available',
      payload: { branch, version }
    });
  }
}
