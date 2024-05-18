import { Component, Input, OnInit } from '@angular/core';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { AuthenticationService } from '@models4insight/authentication';
import { ContextMenuItems } from '@models4insight/components';
import { ProjectPermissionService } from '@models4insight/permissions';
import { PermissionLevel } from '@models4insight/repository';
import { ProjectMembersService } from '@models4insight/services/project';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Component({
  selector: 'models4insight-project-member-table-context-menu',
  templateUrl: 'project-member-table-context-menu.component.html',
  styleUrls: ['project-member-table-context-menu.component.scss']
})
export class ProjectMemberTableContextMenuComponent implements OnInit {
  readonly contextMenuItems: ContextMenuItems = [
    [
      {
        click: () => this.projectMemberService.deleteProjectMember(this.user),
        hasPermission: () => this.handleCheckDeletePermission(),
        holdTime: 1,
        icon: faTimes,
        iconModifier: 'has-text-danger',
        title: 'Delete'
      }
    ]
  ];

  username$: Observable<string>;

  @Input() user: string;

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly projectMemberService: ProjectMembersService,
    private readonly projectPermissionService: ProjectPermissionService
  ) {}

  ngOnInit() {
    this.username$ = this.authenticationService.select([
      'credentials',
      'username'
    ]);
  }

  private handleCheckDeletePermission() {
    const isOwner$ = this.projectPermissionService.checkPermission(
      PermissionLevel.OWNER
    );

    const isMaintainer$ = this.projectPermissionService.checkPermission(
      PermissionLevel.MAINTAINER
    );

    const userPermissions$ = this.projectMemberService.selectMemberPermissions(
      this.user
    );

    const userIsNotOwner$ = combineLatest([
      isMaintainer$,
      userPermissions$
    ]).pipe(
      map(
        ([isMaintainer, userPermissions]) =>
          isMaintainer && userPermissions > PermissionLevel.OWNER
      )
    );

    return combineLatest([isOwner$, userIsNotOwner$]).pipe(
      map(([isOwner, userIsNotOwner]) => isOwner || userIsNotOwner)
    );
  }
}
