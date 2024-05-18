import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { CreateUserGroupModalComponent } from '@models4insight/components';
import { UserGroup } from '@models4insight/repository';
import { ProjectMembersService, ProjectUserGroupsService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

@Component({
  selector: 'models4insight-user-groups-settings',
  templateUrl: 'user-groups.component.html',
  styleUrls: ['user-groups.component.scss']
})
export class UserGroupsSettingsComponent implements OnInit, OnDestroy {
  userGroups$: Observable<UserGroup[]>;
  usernames$: Observable<string[]>;

  @ViewChild(CreateUserGroupModalComponent, { static: true })
  private readonly createUserGroupModal: CreateUserGroupModalComponent;

  constructor(
    private readonly projectMembersService: ProjectMembersService,
    private readonly userGroupsService: ProjectUserGroupsService
  ) {}

  ngOnInit() {
    // Whenever the user group modal is submitted, trigger an update of the repository
    this.createUserGroupModal.submission
      .pipe(untilDestroyed(this))
      .subscribe(group => this.userGroupsService.updateUserGroup(group));

    this.userGroups$ = this.userGroupsService.userGroups.pipe(shareReplay());

    this.usernames$ = this.projectMembersService.members;
  }

  ngOnDestroy() {}

  activateModal() {
    this.createUserGroupModal.activate();
  }

  editGroup(group: UserGroup) {
    this.createUserGroupModal.subject = group;
    this.activateModal();
  }
}
