import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';
import { ModelCompareService } from './model-compare.service';

@Injectable()
export class ModelCompareResolver implements Resolve<void> {
  constructor(private readonly modelCompareService: ModelCompareService) {}

  async resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<void> {
    const baseBranchName = route.queryParamMap.get('baseBranch'),
      otherBranchName = route.queryParamMap.get('otherBranch'),
      baseVersion = route.queryParamMap.get('baseVersion'),
      otherVersion = route.queryParamMap.get('otherVersion');

    this.modelCompareService.compareModels(
      baseBranchName,
      otherBranchName,
      Number.parseInt(baseVersion, 10),
      Number.parseInt(otherVersion, 10)
    );
  }
}
