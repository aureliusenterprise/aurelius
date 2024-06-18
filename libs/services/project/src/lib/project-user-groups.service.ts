import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  deleteUserGroup,
  getUserGroups,
  updateUserGroup,
  UserGroup,
} from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { from, Observable, Subject } from 'rxjs';
import {
  concatMap,
  exhaustMap,
  map,
  mergeMap,
  switchMap,
} from 'rxjs/operators';
import { ProjectService } from './project.service';
import { ServicesProjectModule } from './services-project.module';

export interface ProjectUserGroupsContext {
  readonly userGroupsById?: Dictionary<UserGroup>;
}

export interface ProjectUserGroupsStoreContext {
  readonly isCreatingUserGroup?: boolean;
  readonly isDeletingUserGroup?: boolean;
  readonly isRetrievingUserGroups?: boolean;
  readonly isUpdatingUserGroup?: boolean;
  readonly userGroupsPerProject?: Dictionary<ProjectUserGroupsContext>;
}

export const defaultProjectUserGroupsServiceState: ProjectUserGroupsStoreContext =
  {
    isCreatingUserGroup: false,
    isDeletingUserGroup: false,
    isRetrievingUserGroups: false,
    isUpdatingUserGroup: false,
  };

@Injectable({
  providedIn: ServicesProjectModule,
})
export class ProjectUserGroupsService extends BasicStore<ProjectUserGroupsStoreContext> {
  private readonly createUserGroup$ = new Subject<UserGroup>();
  private readonly deleteUserGroup$ = new Subject<UserGroup>();
  private readonly userGroupDeleted$ = new Subject<void>();
  private readonly userGroupUpdated$ = new Subject<UserGroup>();

  constructor(
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultProjectUserGroupsServiceState,
      name: 'ProjectUserGroupsService',
      storeService,
    });
    this.init();
  }

  private init() {
    // Whenever the project id changes, retrieve the associated user groups
    this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) => this.handleRetrieveUserGroups(projectId)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever a user group create is triggered, handle the create user group operation.
    // Ony one user group create can be active at any time.
    this.createUserGroup$
      .pipe(
        exhaustMap((userGroup) => this.handleCreateUserGroup(userGroup)),
        untilDestroyed(this)
      )
      .subscribe(this.userGroupUpdated$);

    // Whenever a user group delete is triggered, try to delete the given user group
    // A user group can only be deleted by a project owner
    this.deleteUserGroup$
      .pipe(
        exhaustMap((userGroup) => this.handleDeleteUserGroup(userGroup)),
        untilDestroyed(this)
      )
      .subscribe(this.userGroupDeleted$);

    // Whenever a user group is added or updated, save it to the repository
    this.projectService
      .select('projectId')
      .pipe(
        switchMap((projectId) =>
          this.watch(['userGroupsPerProject', projectId, 'userGroupsById'])
        ),
        concatMap((userGroups) => from(userGroups)),
        mergeMap((userGroup) => this.handleUpdateUserGroup(userGroup))
      )
      .subscribe(this.userGroupUpdated$);
  }

  /**
   * Saves the given user group to the back end.
   * Use this function if your user group does not yet have an ID.
   */
  createUserGroup(userGroup: UserGroup) {
    this.updateUserGroup(userGroup);
  }

  /**
   * Deletes the given user group
   */
  deleteUserGroup(userGroup: UserGroup) {
    this.deleteUserGroup$.next(userGroup);
  }

  /**
   * Saves the given user group to the back end.
   */
  async updateUserGroup(userGroup: UserGroup) {
    const projectId = await this.projectService.get('projectId'),
      userGroupId = userGroup?.id;
    if (userGroupId) {
      this.update({
        description: `User group ${userGroupId} updated`,
        path: [
          'userGroupsPerProject',
          projectId,
          'userGroupsById',
          userGroupId,
        ],
        payload: userGroup,
      });
    } else {
      this.createUserGroup$.next(userGroup);
    }
  }

  /**
   * Emits an event whenever a user group has been deleted
   */
  get onUserGroupDeleted(): Observable<void> {
    return this.userGroupDeleted$.asObservable();
  }

  /**
   * Emits an event whenever a user group has been created or changed
   */
  get onUserGroupUpdated(): Observable<UserGroup> {
    return this.userGroupUpdated$.asObservable();
  }

  /**
   * Returns a list of user groups
   */
  get userGroups(): Observable<UserGroup[]> {
    return this.projectService.select('projectId').pipe(
      switchMap((projectId) =>
        this.select(['userGroupsPerProject', projectId, 'userGroupsById'])
      ),
      map(Object.values)
    );
  }

  @ManagedTask('Creating the user group', { isQuiet: true })
  @MonitorAsync('isCreatingUserGroup')
  private async handleCreateUserGroup(userGroup: UserGroup) {
    const projectId = await this.projectService.get('projectId');

    const createUserGroupResponse = await updateUserGroup({
      ...userGroup,
      project_id: projectId,
    }).toPromise();

    this.updateUserGroup(createUserGroupResponse);

    return createUserGroupResponse;
  }

  @ManagedTask('Deleting the user group', { isQuiet: true })
  @MonitorAsync('isDeletingUserGroup')
  private async handleDeleteUserGroup(userGroup: UserGroup) {
    const projectId = await this.projectService.get('projectId'),
      userGroupId = userGroup?.id;

    const deleteUserGroupResponse = await deleteUserGroup(
      projectId,
      userGroupId
    ).toPromise();

    if (deleteUserGroupResponse === 'OK') {
      this.delete({
        description: `User group ${userGroupId} deleted`,
        path: ['userGroupsPerProject', projectId, 'userGroupsById', projectId],
      });
    }
  }

  @ManagedTask('Retrieving the user groups of the current project', {
    isQuiet: true,
  })
  @MonitorAsync('isRetrievingUserGroups')
  private async handleRetrieveUserGroups(projectId: string) {
    const userGroups = await getUserGroups(projectId).toPromise();

    const userGroupsById = indexByProperty(userGroups, 'id');

    this.update({
      description: 'New user groups available',
      path: ['userGroupsPerProject', projectId, 'userGroupsById'],
      payload: userGroupsById,
    });
  }

  @ManagedTask('Saving the user group', { isQuiet: true })
  @MonitorAsync('isUpdatingUserGroup')
  private async handleUpdateUserGroup(userGroup: UserGroup) {
    return updateUserGroup(userGroup).toPromise();
  }
}
