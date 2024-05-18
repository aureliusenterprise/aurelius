import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { UserSearchModalComponent } from '@models4insight/components';
import { PermissionLevel, Project } from '@models4insight/repository';
import { ProjectMembersService, ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';

@Component({
  selector: 'models4insight-project-member-settings',
  templateUrl: 'project-members.component.html',
  styleUrls: ['project-members.component.scss']
})
export class ProjectMemberSettingsComponent implements OnInit, OnDestroy {
  project$: Observable<Project>;
  usernames$: Observable<string[]>;

  @ViewChild(UserSearchModalComponent, { static: true })
  private readonly userSearchModal: UserSearchModalComponent;

  constructor(
    private readonly projectMembersService: ProjectMembersService,
    private readonly projectService: ProjectService
  ) {}

  ngOnInit() {
    this.project$ = this.projectService.selectCurrentProject();
    this.usernames$ = this.projectMembersService.members;

    // Whenever a new user is selected in the user search modal, add them to the project as a business user
    this.userSearchModal.user
      .pipe(untilDestroyed(this))
      .subscribe(user =>
        this.projectMembersService.addProjectMember(
          user.userName,
          PermissionLevel.BUSINESS_USER
        )
      );
  }

  ngOnDestroy() {}

  activateModal() {
    this.userSearchModal.activate();
  }
}
