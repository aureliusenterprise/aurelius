import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { Branch, getBranches, getProvenance, ModelProvenance, Project } from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty } from '@models4insight/utils';
import { Dictionary, orderBy } from 'lodash';
import { Subject } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

export interface GenerateReportStoreContext {
  readonly isLoadingVersions?: boolean;
  readonly versionsByTimestamp?: Dictionary<ModelProvenance>;
}

export const projectServiceDefaultState: GenerateReportStoreContext = {
  isLoadingVersions: false
};

@Injectable()
export class GenerateReportService extends BasicStore<
  GenerateReportStoreContext
> {
  private loadVersions$: Subject<[Project, Branch]> = new Subject<
    [Project, Branch]
  >();

  constructor(storeService: StoreService) {
    super({
      defaultState: projectServiceDefaultState,
      name: 'ProjectService',
      storeService
    });
    this.init();
  }

  loadVersions(project: Project, branch: Branch) {
    this.loadVersions$.next([project, branch]);
  }

  get versions() {
    return this.select('versionsByTimestamp').pipe(
      map(versions =>
        orderBy(Object.values(versions), ['start_date'], ['desc'])
      )
    );
  }

  private init() {
    // Whenever a branch is selected, load the provenance for that branch
    this.loadVersions$
      .pipe(
        switchMap(([project, branch]) =>
          this.handleLoadVersions(branch, project)
        )
      )
      .subscribe();
  }

  @ManagedTask('Loading the model versions for the selected branch', {
    isQuiet: true
  })
  @MonitorAsync('isLoadingVersions')
  private async handleLoadVersions(branch: Branch, project: Project) {
    const versions =
      branch && project
        ? await getProvenance(project.project, {
            branchName: branch.name,
            forceUpdate: true
          }).toPromise()
        : [];

    const versionsByTimestamp = indexByProperty(versions, 'start_date');

    this.update({
      description: `New provenance available`,
      payload: { versionsByTimestamp }
    });
  }
}
