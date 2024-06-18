import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import {
  ProjectMembersService,
  ProjectUserGroupsService,
} from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

export interface CreateBranchModalStoreContext {
  readonly nameTypeIndex?: Dictionary<'user' | 'group'>;
}

export const createBranchModalServiceDefaultState: CreateBranchModalStoreContext =
  {
    nameTypeIndex: {},
  };

@Injectable()
export class CreateBranchModalService extends BasicStore<CreateBranchModalStoreContext> {
  constructor(
    private readonly projectMembersService: ProjectMembersService,
    private readonly projectUserGroupsService: ProjectUserGroupsService
  ) {
    super({ defaultState: createBranchModalServiceDefaultState });
    this.init();
  }

  private init() {
    const usernames = this.projectMembersService.members;
    const userGroups = this.projectUserGroupsService.userGroups.pipe(
      map((groups) => groups.map((group) => group.name))
    );

    // Whenever the usernames or user groups update, create a new name type index
    combineLatest([usernames, userGroups])
      .pipe(
        switchMap(([names, groups]) => this.createNameTypeIndex(names, groups)),
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
