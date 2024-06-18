import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { PermissionLevel } from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Observable, Subject } from 'rxjs';
import { concatMap, map, switchMap } from 'rxjs/operators';
import { ProjectService } from './project.service';
import { ProjectsService } from './projects.service';
import { ServicesProjectModule } from './services-project.module';

export interface ProjectMembersStoreContext {
  readonly isUpdatingMemberPermissions?: boolean;
}

export const defaultProjectMembersServiceState: ProjectMembersStoreContext = {
  isUpdatingMemberPermissions: false,
};

@Injectable({
  providedIn: ServicesProjectModule,
})
export class ProjectMembersService extends BasicStore {
  private readonly deleteProjectMember$ = new Subject<string>();
  private readonly projectMemberDeleted$ = new Subject<string>();
  private readonly updateProjectMember$ = new Subject<
    [string, PermissionLevel]
  >();
  private readonly projectMemberUpdated$ = new Subject<
    Dictionary<PermissionLevel>
  >();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly projectService: ProjectService,
    private readonly projectsService: ProjectsService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultProjectMembersServiceState,
      name: 'ProjectMembersService',
      storeService,
    });
    this.init();
  }

  private init() {
    this.deleteProjectMember$
      .pipe(
        concatMap((username) => this.handleDeleteProjectMember(username)),
        untilDestroyed(this)
      )
      .subscribe(this.projectMemberDeleted$);

    this.updateProjectMember$
      .pipe(
        concatMap(([username, permission]) =>
          this.handleUpdateMemberPermissions(username, permission)
        ),
        untilDestroyed(this)
      )
      .subscribe(this.projectMemberUpdated$);
  }

  /**
   * Add the member with the given `username` to the current project with the given `permission` level.
   * By default, their permission level will be set to `BUSINESS_USER`.
   *
   * @param username The username of the new project member
   * @param permission The permission level of the new project member
   */
  addProjectMember(
    username: string,
    permission: PermissionLevel = PermissionLevel.BUSINESS_USER
  ) {
    this.setProjectMemberPermissions(username, permission);
  }

  /**
   * Removes the member with the given username from the project.
   *
   * @param username The username of the project member.
   */
  deleteProjectMember(username: string) {
    this.deleteProjectMember$.next(username);
  }

  /**
   * Returns a snapshot of the current user's permission level as a `Promise`.
   */
  async getCurrentUserPermissions() {
    const username = await this.authenticationService.get([
      'credentials',
      'username',
    ]);

    return this.getMemberPermissions(username);
  }

  /**
   * Returns a snapshot of the permission level of the user with the given `username` as a `Promise`.
   */
  async getMemberPermissions(username: string) {
    const projectId = await this.projectService.get('projectId');

    return this.projectsService.get(
      ['projectsById', projectId, 'permissions', username],
      { includeFalsy: true }
    );
  }

  /**
   * Returns an `Observable` stream of the current user's permission level.
   */
  selectCurrentUserPermissions() {
    return this.authenticationService
      .select(['credentials', 'username'])
      .pipe(switchMap((username) => this.selectMemberPermissions(username)));
  }

  /**
   * Returns an `Observable` stream of the permission level of the project member with the given `username`.
   */
  selectMemberPermissions(username: string) {
    return this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.projectsService.select([
            'projectsById',
            projectId,
            'permissions',
            username,
          ])
        )
      );
  }

  /**
   * Updates the `permission` level of the user with the given `username`.
   *
   * @param username The username of the new project member
   * @param permission The permission level of the new project member
   */
  setProjectMemberPermissions(username: string, permission: PermissionLevel) {
    this.updateProjectMember$.next([username, permission]);
  }

  /** Returns a list of project members */
  get members() {
    return this.projectService
      .selectCurrentProject()
      .pipe(map((project) => Object.keys(project.permissions)));
  }

  /**
   * Emits an event whenever a project member has been deleted
   */
  get onProjectMemberDeleted(): Observable<string> {
    return this.projectMemberDeleted$.asObservable();
  }

  /**
   * Emits an event whenever a project member has been created or changed
   */
  get onProjectMemberUpdated(): Observable<Dictionary<PermissionLevel>> {
    return this.projectMemberUpdated$.asObservable();
  }

  @ManagedTask("Updating the project member's permissions", { isQuiet: true })
  @MonitorAsync('isUpdatingMemberPermissions')
  private async handleUpdateMemberPermissions(
    username: string,
    permission: PermissionLevel
  ) {
    const projectId = await this.projectService.get('projectId');

    this.projectsService.update({
      description: `Updated permissions for user ${username} to project ${projectId}`,
      path: ['projectsById', projectId, 'permissions', username],
      payload: permission,
    });

    return { username: permission };
  }

  @ManagedTask('Deleting the project member', { isQuiet: true })
  @MonitorAsync('isDeletingProjectMember')
  private async handleDeleteProjectMember(username: string) {
    const projectId = await this.projectService.get('projectId');

    this.projectsService.delete({
      description: `Removed permissions for user ${username} to project ${projectId}`,
      path: ['projectsById', projectId, 'permissions', username],
    });

    return username;
  }
}
