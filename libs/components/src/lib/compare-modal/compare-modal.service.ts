import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import {
  Branch,
  getProvenance,
  ModelProvenance,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Observable, Subject } from 'rxjs';
import { map } from 'rxjs/operators';

export interface CompareModalStoreContext {
  readonly isLoadingVersions?: boolean;
  readonly versions?: Dictionary<ModelProvenance>;
}

export const defaultCompareModalServiceState: CompareModalStoreContext = {
  isLoadingVersions: false,
};

@Injectable()
export class CompareModalService extends BasicStore<CompareModalStoreContext> {
  private readonly loadVersions$ = new Subject<Branch>();

  constructor(private readonly projectService: ProjectService) {
    super({ defaultState: defaultCompareModalServiceState });
    this.init();
  }

  /**
   * Triggers the retrieve process for the other  versions based on the given branch
   * @param branch the branch for which to retrieve the versions
   */
  loadVersions(branch: Branch) {
    this.loadVersions$.next(branch);
  }

  /**
   * Returns an `Observable` stream of the model provenance for the currently selected branch
   */
  get versions(): Observable<ModelProvenance[]> {
    return this.select('versions').pipe(map(Object.values));
  }

  private init() {
    this.loadVersions$
      .pipe(untilDestroyed(this))
      .subscribe((branch) => this.handleLoadOtherVersions(branch));
  }

  @ManagedTask('Loading the model versions for the selected branch', {
    isQuiet: true,
  })
  @MonitorAsync('isLoadingVersions')
  private async handleLoadOtherVersions(branch: Branch) {
    const project = await this.projectService.getCurrentProject();

    const versions = branch
      ? await getProvenance(project.project, {
          branchName: branch.name,
        }).toPromise()
      : [];

    const versionsByStartDate = indexByProperty(versions, 'start_date');

    this.update({
      description: `New versions available`,
      payload: { versions: versionsByStartDate },
    });
  }
}
