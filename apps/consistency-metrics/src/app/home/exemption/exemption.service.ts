import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { Branch, getBranches, getProvenance, ModelProvenance, Project } from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { Subject } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export interface ExemptionStoreContext {
  readonly branches?: Branch[];
  readonly isLoadingBranches?: boolean;
  readonly isLoadingVersions?: boolean;
  readonly versions?: ModelProvenance[];
}

export const exemptionServiceDefaultState: ExemptionStoreContext = {
  isLoadingBranches: false,
  isLoadingVersions: false
};

@Injectable()
export class ExemptionService extends BasicStore<ExemptionStoreContext> {
  private loadBranches$: Subject<Project> = new Subject<Project>();
  private loadVersions$: Subject<[Project, Branch]> = new Subject<
    [Project, Branch]
  >();

  constructor(storeService: StoreService) {
    super({
      defaultState: exemptionServiceDefaultState,
      name: 'ExemptionService',
      storeService
    });
    this.init();
  }

  loadBranches(project: Project) {
    this.loadBranches$.next(project);
  }

  loadVersions(project: Project, branch: Branch) {
    this.loadVersions$.next([project, branch]);
  }

  private init() {
    // Whenever a project is selected, load the branches for that project
    this.loadBranches$
      .pipe(switchMap(project => this.handleLoadBranches(project)))
      .subscribe();

    // Whenever a branch is selected, load the provenance for that branch
    this.loadVersions$
      .pipe(
        switchMap(([project, branch]) =>
          this.handleLoadVersions(branch, project)
        )
      )
      .subscribe();
  }

  @ManagedTask('Loading the branches for the selected project')
  @MonitorAsync('isLoadingBranches')
  private async handleLoadBranches(project: Project) {
    const branches = project
      ? await getBranches(project.id, {
          forceUpdate: true
        }).toPromise()
      : [];

    this.update({
      description: `New branches available`,
      payload: {
        branches
      }
    });
  }

  @ManagedTask('Loading the model versions for the selected branch')
  @MonitorAsync('isLoadingVersions')
  private async handleLoadVersions(branch: Branch, project: Project) {
    const versions =
      branch && project
        ? await getProvenance(project.project, {
            branchName: branch.name,
            forceUpdate: true
          }).toPromise()
        : [];

    this.update({
      description: `New provenance available`,
      payload: { versions }
    });
  }
}
