import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { UserGroup } from '@models4insight/repository';
import {
  ProjectMembersService,
  ProjectService,
  ProjectUserGroupsService,
} from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

export interface CreateUserGroupModalStoreContext {
  readonly connectedGroups?: string[];
  readonly currentGroupName?: string;
  readonly nameTypeIndex?: Dictionary<'user' | 'group'>;
}

/**
 * Returns the names of the groups which are connected to the group with the given name
 */
function findConnectedGroups(
  /** The name of the group for which to find the connected groups */
  groupName: string,
  /** All existing groups indexed by name */
  groupsByName: Dictionary<UserGroup>
): string[] {
  // Checks whether the given group, or any of its members, are connected to the given group
  const isConnected = ({ members = [] }: UserGroup, visited: string[] = []) => {
    return (
      members.includes(groupName) ||
      members
        .filter((member) => member in groupsByName && !visited.includes(member))
        .some((member) =>
          isConnected(groupsByName[member], [...visited, ...members])
        )
    );
  };

  return Object.values(groupsByName)
    .filter((group) => isConnected(group))
    .map(({ name }) => name);
}

@Injectable()
export class CreateUserGroupModalService extends BasicStore<CreateUserGroupModalStoreContext> {
  constructor(
    private readonly projectService: ProjectService,
    private readonly projectMembersService: ProjectMembersService,
    private readonly projectUserGroupsService: ProjectUserGroupsService
  ) {
    super();
    this.init();
  }

  private init() {
    // Whenever the current group name updates, or the groups index updates, find all groups connected to the current group
    combineLatest([
      this.select('currentGroupName'),
      this.projectService
        .select('projectId')
        .pipe(
          switchMap((projectId) =>
            this.projectUserGroupsService.select([
              'userGroupsPerProject',
              projectId,
              'userGroupsById',
            ])
          )
        ),
    ])
      .pipe(
        map(([currentGroupName, groups]) =>
          findConnectedGroups(currentGroupName, groups)
        ),
        untilDestroyed(this)
      )
      .subscribe((connectedGroups) =>
        this.update({
          description: 'New connected groups available',
          payload: { connectedGroups },
        })
      );

    // Whenever the project members or user group names change, update the name type index
    combineLatest([
      this.projectMembersService.members,
      this.projectUserGroupsService.userGroups.pipe(
        map((groups) => groups.map((group) => group.name))
      ),
    ])
      .pipe(
        switchMap(([users, groups]) => this.createNameTypeIndex(users, groups)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  private async createNameTypeIndex(users: string[], groups: string[]) {
    const nameTypeIndex = {
      ...users.reduce((index, user) => ({ ...index, [user]: 'user' }), {}),
      ...groups.reduce((index, group) => ({ ...index, [group]: 'group' }), {}),
    };

    this.update({
      description: 'New name type index available',
      payload: { nameTypeIndex },
    });
  }
}
