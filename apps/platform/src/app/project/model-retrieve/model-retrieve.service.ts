import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { BranchSummary, ModelProvenance } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { sumBy } from 'lodash';
import { map } from 'rxjs/operators';

export interface FilterContext {
  readonly pageIndex?: number;
  readonly search?: string;
  readonly from?: number;
  readonly until?: number;
  readonly latestOnly?: boolean;
  readonly branch?: string;
}

export interface ModelRetrieveStoreContext {
  readonly branches?: BranchSummary[];
  readonly modelCount?: number;
  readonly filter?: FilterContext;
  readonly models?: ModelProvenance[];
}

@Injectable()
export class ModelRetrieveService extends BasicStore<
  ModelRetrieveStoreContext
> {
  constructor(
    private projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      name: 'ModelRetrieveService',
      storeService
    });
    this.init();
  }

  private init() {
    // Whenever the list of branches updates, calculate the total amount of modals for use with the provenance table paging
    this.select('branches')
      .pipe(map(branches => sumBy(branches, 'cnt')))
      .subscribe(modelCount =>
        this.update({
          description: 'Total model history length updated',
          payload: {
            modelCount
          }
        })
      );

    // Whenever the project id changes, reset the store
    this.projectService.select('projectId').subscribe(() => this.reset());
  }
}
