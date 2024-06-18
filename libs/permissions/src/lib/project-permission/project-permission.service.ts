import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import {
  getUserRole,
  ProjectPermissionLevel,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { Observable, of } from 'rxjs';
import {
  concatMap,
  distinctUntilKeyChanged,
  map,
  switchMap,
  takeUntil,
} from 'rxjs/operators';

export interface ProjectPermissionStoreContext {
  readonly permissions?: {
    readonly [projectId: string]: ProjectPermissionLevel;
  };
}

@Injectable()
export class ProjectPermissionService extends BasicStore<ProjectPermissionStoreContext> {
  constructor(
    private projectService: ProjectService,
    storeService: StoreService
  ) {
    super({ name: 'ProjectPermissionService', storeService });
    this.init();
  }

  private init() {
    // Handles control flow to prevent flooding the rest api with requests for the same project.
    // After the first request is made for any project ID, any further requests can be served from the store.
    this.projectService
      .selectCurrentProject()
      .pipe(
        distinctUntilKeyChanged('id'),
        concatMap(({ project }) =>
          // This manages control flow for updates on the store to ensure there are no excess updates due to triggers in quick succession
          of(1).pipe(
            switchMap(() => this.handleCheckPermissions(project)),
            takeUntil(this.select(['permissions', project]))
          )
        )
      )
      .subscribe();
  }

  /**
   * Returns an `Observable`stream of whether or not the current user meets the given minimum required permission level for the current project.
   * @param requiredPermissionLevel The minimum permission level required.
   */
  checkPermission(
    requiredPermissionLevel: ProjectPermissionLevel
  ): Observable<boolean> {
    return this.projectService.selectCurrentProject().pipe(
      switchMap(({ project }) => this.select(['permissions', project])),
      map((permissionLevel) => permissionLevel <= requiredPermissionLevel)
    );
  }

  /**
   * Returns whether or not the current huser meets the given minimum required permission level for the current project
   * @param requiredPermissionLevel The minimum permission level required.
   */
  async hasPermission(requiredPermissionLevel: ProjectPermissionLevel) {
    const { project } = await this.projectService.getCurrentProject(),
      permissionLevel = await this.get(['permissions', project]);

    return permissionLevel <= requiredPermissionLevel;
  }

  private async handleCheckPermissions(projectName: string) {
    const { role_id } = await getUserRole(projectName, {
      forceUpdate: true,
    }).toPromise();

    this.update({
      description: `Permission level updated for project ${projectName}`,
      path: ['permissions', projectName],
      payload: role_id,
    });
  }
}
