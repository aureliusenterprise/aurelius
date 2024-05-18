import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { PermissionLevel, UserGroup } from '@models4insight/repository';

const userGroupTableConfig: SortableTableShellConfig = {
  name: {
    displayName: 'Group name',
    description: 'The name of the user group'
  },
  size: {
    displayName: 'Group size',
    description: 'The total number of members of this user group',
    isStatic: true
  },
  description: {
    displayName: 'Description',
    description: 'The description of this user group'
  },
  permission: {
    displayName: 'Access rights',
    description:
      'The level of project access given to members of this user group',
    isStatic: true
  },
  context_menu: { isStatic: true }
};

@Component({
  selector: 'models4insight-user-group-table',
  templateUrl: 'user-group-table.component.html',
  styleUrls: ['user-group-table.component.scss']
})
export class UserGroupTableComponent extends AbstractSortableTable
  implements OnInit {
  @Output() edit: EventEmitter<UserGroup> = new EventEmitter<UserGroup>();

  PermissionLevel = PermissionLevel;

  constructor() {
    super();
  }

  ngOnInit() {
    this.config = userGroupTableConfig;
  }

  onEdit(group: UserGroup) {
    this.edit.emit(group);
  }
}
