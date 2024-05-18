import { Component, Input, OnInit } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { PermissionLevel, Project } from '@models4insight/repository';
import { ProjectMembersService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

const membersTableConfig: SortableTableShellConfig = {
  username: {
    displayName: 'Username',
    description: 'The name of the user'
  },
  permission: {
    displayName: 'Permission level',
    description:
      'The permission level defines which actions the user is allowed to do in the project',
    isStatic: true
  },
  context_menu: {
    isStatic: true
  }
};

export interface ProjectMember {
  readonly username?: string;
}

@Component({
  selector: 'models4insight-project-member-table',
  templateUrl: 'project-member-table.component.html',
  styleUrls: ['project-member-table.component.scss']
})
export class ProjectMemberTableComponent extends AbstractSortableTable
  implements OnInit {
  @Input() project: Project;

  readonly PermissionLevel = PermissionLevel;

  username$: Observable<string>;
  members$: Observable<ProjectMember[]>;

  membersTableConfig = membersTableConfig;

  constructor(
    private readonly autheticationService: AuthenticationService,
    private readonly projectMemberService: ProjectMembersService
  ) {
    super();
  }

  ngOnInit() {
    this.members$ = this.projectMemberService.members.pipe(
      map(members =>
        members.map(username => ({
          username
        }))
      )
    );
    this.username$ = this.autheticationService.select([
      'credentials',
      'username'
    ]);
  }

  onSetUserPermissions(username: string, permission: PermissionLevel) {
    this.projectMemberService.setProjectMemberPermissions(username, permission);
  }
}
