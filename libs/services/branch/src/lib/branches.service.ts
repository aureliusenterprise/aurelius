import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  Branch,
  deleteBranch,
  getBranches,
  updateBranch,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { from, Observable, Subject } from 'rxjs';
import { concatMap, map, mergeMap, switchMap } from 'rxjs/operators';
import { ServicesBranchModule } from './services-branch.module';

export interface ProjectBranchesContext {
  readonly branchesById?: Dictionary<Branch>;
  readonly branchesByName?: Dictionary<Branch>;
}

export interface BranchesStoreContext {
  readonly branchesPerProject?: Dictionary<ProjectBranchesContext>;
  readonly isCreatingBranch?: boolean;
  readonly isDeletingBranch?: boolean;
  readonly isIndexingBranchesByName?: boolean;
  readonly isLoadingBranches?: boolean;
  readonly isUpdatingBranch?: boolean;
}

export const defaultBranchesServiceState: BranchesStoreContext = {
  isCreatingBranch: false,
  isDeletingBranch: false,
  isIndexingBranchesByName: false,
  isLoadingBranches: false,
  isUpdatingBranch: false,
};

@Injectable({
  providedIn: ServicesBranchModule,
})
export class BranchesService extends BasicStore<BranchesStoreContext> {
  private readonly deleteBranch$ = new Subject<Branch>();
  private readonly branchDeleted$ = new Subject<void>();
  private readonly createBranch$ = new Subject<Branch>();
  private readonly branchUpdated$ = new Subject<Branch>();

  constructor(
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultBranchesServiceState,
      name: 'BranchesService',
      storeService,
    });
    this.init();
  }

  private init() {
    this.deleteBranch$
      .pipe(
        concatMap((branch) => this.handleDeleteBranch(branch)),
        untilDestroyed(this)
      )
      .subscribe(this.branchDeleted$);

    this.createBranch$
      .pipe(
        concatMap((branch) => this.handleCreateBranch(branch)),
        untilDestroyed(this)
      )
      .subscribe(this.branchUpdated$);

    // Whenever a new project is selected, retrieve the branches for that project
    this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) => this.handleRetrieveBranches(projectId)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the branches update, build an index of branches by name
    this.branches
      .pipe(
        switchMap((branches) => this.handleIndexBranchesByName(branches)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever a branch is created or updated, save it to the backend
    this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.watch(['branchesPerProject', projectId, 'branchesById'])
        ),
        concatMap((branches) => from(branches)),
        mergeMap((branch) => this.handleUpdateBranch(branch)),
        untilDestroyed(this)
      )
      .subscribe(this.branchUpdated$);
  }

  /**
   * Saves the given `branch` to the back end.
   * Use this function if your `branch` does not yet have an ID.
   */
  createBranch(branch: Branch) {
    this.updateBranch(branch);
  }

  /**
   * Deletes the given `branch`
   */
  deleteBranch(branch: Branch) {
    this.deleteBranch$.next(branch);
  }

  /**
   * Returns a snapshot of the `Branch` with the given `branchId` as a `Promise`.
   * @param branchId the ID of the `Branch` to retrieve.
   */
  async getBranchById(branchId: string) {
    const projectId = await this.projectService.get('projectId');
    return this.get([
      'branchesPerProject',
      projectId,
      'branchesById',
      branchId,
    ]);
  }

  /**
   * Returns a snapshot of the `Branch` with the given `branchName` as a `Promise`.
   * @param branchName The name of the `Branch` to retrieve.
   */
  async getBranchByName(branchName: string) {
    const projectId = await this.projectService.get('projectId');
    return this.get([
      'branchesPerProject',
      projectId,
      'branchesByName',
      branchName,
    ]);
  }

  /**
   * Returns an `Observable` stream of the `Branch` with the given `branchId`.
   * @param branchId the ID of the `Branch` to observe
   */
  selectBranchById(branchId: string) {
    return this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.select([
            'branchesPerProject',
            projectId,
            'branchesById',
            branchId,
          ])
        )
      );
  }

  /**
   * Returns an `Observable` stream of the `Branch` with the given `branchName`.
   * @param branchName The name of the `Branch` to observe.
   */
  selectBranchByName(branchName: string) {
    return this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.select([
            'branchesPerProject',
            projectId,
            'branchesByName',
            branchName,
          ])
        )
      );
  }

  /**
   * Saves the given `branch` to the back end.
   */
  async updateBranch(branch: Branch) {
    const projectId = await this.projectService.get('projectId'),
      branchId = branch?.id;
    if (branchId) {
      this.update({
        description: `Branch ${branchId} updated`,
        path: ['branchesPerProject', projectId, 'branchesById', branchId],
        payload: branch,
      });
    } else {
      this.createBranch$.next(branch);
    }
  }

  /**
   * Returns an `Observable` stream of all branches as a list
   */
  get branches(): Observable<Branch[]> {
    return this.projectService.select('projectId').pipe(
      switchMap((projectId) =>
        this.select(['branchesPerProject', projectId, 'branchesById'])
      ),
      map(Object.values)
    );
  }

  @ManagedTask('Creating the branch', { isQuiet: true })
  @MonitorAsync('isCreatingBranch')
  private async handleCreateBranch(branch: Branch) {
    const projectId = await this.projectService.get('projectId');

    const createBranchResponse = await updateBranch({
      ...branch,
      project_id: projectId,
    }).toPromise();

    this.updateBranch(createBranchResponse);

    return createBranchResponse;
  }

  @ManagedTask('Deleting the branch', { isQuiet: true })
  @MonitorAsync('isDeletingBranch')
  private async handleDeleteBranch(branch: Branch) {
    const projectId = await this.projectService.get('projectId'),
      branchId = branch?.id;

    const deleteBranchResponse = await deleteBranch(
      projectId,
      branchId
    ).toPromise();

    if (deleteBranchResponse === 'OK') {
      this.delete({
        description: `Branch ${branchId} deleted`,
        path: ['branchesPerProject', projectId, 'branchesById', branchId],
      });
    }
  }

  @ManagedTask('Indexing the branches by name', { isQuiet: true })
  @MonitorAsync('isIndexingBranchesByName')
  private async handleIndexBranchesByName(branches: Branch[]) {
    const projectId = await this.projectService.get('projectId'),
      branchesByName = indexByProperty(branches, 'name');

    this.update({
      description: 'New branches by name index available',
      path: ['branchesPerProject', projectId, 'branchesByName'],
      payload: branchesByName,
    });
  }

  @ManagedTask('Retrieving the branches for the current project', {
    isQuiet: true,
  })
  @MonitorAsync('isLoadingBranches')
  private async handleRetrieveBranches(projectId: string) {
    const branches = await getBranches(projectId, {
      forceUpdate: true,
    }).toPromise();

    const branchesById = indexByProperty(branches, 'id');

    this.update({
      description: 'New branches available',
      path: ['branchesPerProject', projectId, 'branchesById'],
      payload: branchesById,
    });
  }

  @ManagedTask('Saving the branch', { isQuiet: true })
  @MonitorAsync('isUpdatingBranch')
  private async handleUpdateBranch(branch: Branch) {
    const projectId = await this.projectService.get('projectId');
    return updateBranch({ ...branch, project_id: projectId }).toPromise();
  }
}
