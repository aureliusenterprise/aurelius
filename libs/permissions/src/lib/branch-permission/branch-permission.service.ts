import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import {
  BranchPermissionLevel,
  PermissionLevel,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { combineLatest, Observable, of, Subject } from 'rxjs';
import {
  concatMap,
  map,
  switchMap,
  takeUntil,
  withLatestFrom,
} from 'rxjs/operators';
import { ProjectPermissionService } from '../project-permission';

export interface BranchPermissionStoreContext {
  readonly permissions?: {
    readonly [project: string]: {
      readonly [branch: string]: BranchPermissionLevel;
    };
  };
}

@Injectable()
export class BranchPermissionService extends BasicStore<BranchPermissionStoreContext> {
  private readonly checkPermission$ = new Subject<string>();

  constructor(
    private readonly projectService: ProjectService,
    private readonly projectPermissionService: ProjectPermissionService,
    storeService: StoreService
  ) {
    super({ name: 'BranchPermissionService', storeService });
    this.init();
  }

  private init() {
    // Handles control flow to prevent flooding the rest api with requests for the same project.
    // After the first request is made for any combination of project ID and branch name, any further requests can be served from the store.
    this.checkPermission$
      .pipe(
        withLatestFrom(this.projectService.select('projectId')),
        concatMap(([branchName, projectId]) =>
          // This manages control flow for updates on the store to ensure there are no excess updates due to triggers in quick succession
          of(1).pipe(
            switchMap(() => this.handleCheckPermission(projectId, branchName)),
            takeUntil(this.select(['permissions', projectId, branchName]))
          )
        )
      )
      .subscribe();
  }

  /**
   * Checks whether or not the current user meets the required permission level for the branch of the given project. The owner of a project always has the required permissions.
   * @param project the project to check permission for
   * @param branchName the branch to check permission for
   * @param requiredPermissionLevel the minimum permission level required
   */
  checkPermission(
    branchName: string,
    requiredPermissionLevel: BranchPermissionLevel
  ): Observable<boolean> {
    this.checkPermission$.next(branchName);

    const branchPermissionLevel = this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.select(['permissions', projectId, branchName])
        )
      );

    const isOwner = this.projectPermissionService.checkPermission(
      PermissionLevel.OWNER
    );

    return combineLatest([branchPermissionLevel, isOwner]).pipe(
      map(
        ([branchPermissionLevel, isOwner]) =>
          branchPermissionLevel <= requiredPermissionLevel || isOwner
      )
    );
  }

  private async handleCheckPermission(projectId: string, branchName: string) {
    // Placeholder while rest api function is still unavailable.
    this.update({
      description: `Permission level updated for branch ${branchName} of project ${projectId}`,
      path: ['permissions', projectId, branchName],
      payload: PermissionLevel.OWNER,
    });
  }
}
