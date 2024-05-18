import { Injectable, OnDestroy } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { Branch, getBranches, getMetricExemption, getProvenance, MetricExemption, ModelProvenance, Project } from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Subject } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export interface ExemptionsStoreContext {
  readonly branches?: Branch[];
  readonly exemptions?: MetricExemption[];
  readonly isLoadingBranches?: boolean;
  readonly isLoadingExemptions?: boolean;
  readonly isLoadingVersions?: boolean;
  readonly projects?: Project[];
  readonly versions?: ModelProvenance[];
}

export const exemptionsServiceDefaultState: ExemptionsStoreContext = {
  isLoadingBranches: false,
  isLoadingVersions: false
};

// TODO: Add Angular decorator.
@Injectable()
export class ExemptionsService extends BasicStore<ExemptionsStoreContext>
  implements OnDestroy {
  private loadBranches$: Subject<Project> = new Subject<Project>();
  private loadVersions$: Subject<[Project, Branch]> = new Subject<
    [Project, Branch]
  >();
  private loadExemptions$: Subject<
    [Project, Branch, ModelProvenance]
  > = new Subject<[Project, Branch, ModelProvenance]>();

  constructor() {
    super({
      defaultState: exemptionsServiceDefaultState
    });
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    // Whenever a project is selected, load the branches for that project
    this.loadBranches$
      .pipe(
        switchMap(project => this.handleLoadBranches(project)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever a branch is selected, load the provenance for that branch
    this.loadVersions$
      .pipe(
        switchMap(([project, branch]) =>
          this.handleLoadVersions(branch, project)
        ),
        untilDestroyed(this)
      )
      .subscribe();

    // Retrieve exemptions for a given project, branch and version
    this.loadExemptions$
      .pipe(
        switchMap(([project, branch, version]) =>
          this.handleLoadExemptions(project, branch, version)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  loadBranches(project: Project) {
    this.loadBranches$.next(project);
  }

  loadVersions(project: Project, branch: Branch) {
    this.loadVersions$.next([project, branch]);
  }

  loadExemptions(project: Project, branch?: Branch, version?: ModelProvenance) {
    this.loadExemptions$.next([project, branch, version]);
  }

  @ManagedTask('Loading the branches for the selected project', {
    isQuiet: true
  })
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

    this.update({
      description: `New provenance available`,
      payload: { versions }
    });
  }

  @ManagedTask('Loading the exemptions')
  @MonitorAsync('isLoadingExemptions')
  private async handleLoadExemptions(
    project: Project,
    branch: Branch,
    version: ModelProvenance
  ) {
    const exemptions = await getMetricExemption(project.id, {
      branchId: branch ? branch.id : null,
      forceUpdate: true,
      version: version ? version.start_date : null
    }).toPromise();

    this.update({
      description: `New exemptions available`,
      payload: { exemptions }
    });
  }
}
