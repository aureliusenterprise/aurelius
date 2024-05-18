import { Component, EventEmitter, Input, Output } from '@angular/core';
import { faEdit, faTimes } from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';
import { ProjectPermissionService } from '@models4insight/permissions';
import { PermissionLevel, Project, UserGroup } from '@models4insight/repository';
import { ProjectUserGroupsService } from '@models4insight/services/project';

export interface UserGroupRowContext {
  project: Project;
  group: UserGroup;
}

@Component({
  // tslint:disable-next-line: component-selector
  selector: 'models4insight-user-group-context-menu',
  templateUrl: 'user-group-context-menu.component.html',
  styleUrls: ['user-group-context-menu.component.scss']
})
export class UserGroupContextMenuComponent {
  @Output() edit: EventEmitter<UserGroup> = new EventEmitter<UserGroup>();

  contextMenuItems: ContextMenuItems = [];
  group: UserGroup;
  project: Project;

  PermissionLevel = PermissionLevel;

  constructor(
    private readonly userGroupsService: ProjectUserGroupsService,
    private readonly projectPermissionService: ProjectPermissionService
  ) {}

  removeUserGroup(group: UserGroup) {
    this.userGroupsService.deleteUserGroup(group);
  }

  @Input()
  set context(group: UserGroup) {
    this.group = group;
    this.contextMenuItems = this.createContextMenuItems(group);
  }

  private createContextMenuItems(group: UserGroup): ContextMenuItems {
    return [
      [
        {
          click: () => this.edit.emit(group),
          hasPermission: () =>
            this.projectPermissionService.checkPermission(
              PermissionLevel.CONTRIBUTOR
            ),
          icon: faEdit,
          iconModifier: 'has-text-primary',
          title: 'Edit'
        }
      ],
      [
        {
          click: () => this.removeUserGroup(group),
          hasPermission: () =>
            this.projectPermissionService.checkPermission(
              PermissionLevel.OWNER
            ),
          holdTime: 1,
          icon: faTimes,
          iconModifier: 'has-text-danger',
          title: 'Delete'
        }
      ]
    ];
  }
}
