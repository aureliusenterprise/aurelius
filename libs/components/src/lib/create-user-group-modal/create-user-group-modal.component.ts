import { Component, OnInit } from '@angular/core';
import {
  UntypedFormArray,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import {
  faInfo,
  faShieldAlt,
  faUserCog,
  faUserPlus,
} from '@fortawesome/free-solid-svg-icons';
import { UserGroup } from '@models4insight/repository';
import { ProjectUserGroupsService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AbstractModalForm } from '../abstract-modal-form/abstract-modal-form';
import {
  defaultDescriptionInputContext,
  DescriptionInput,
  DescriptionInputContext,
} from '../description-input';
import { ModalContext } from '../modal';
import { CreateUserGroupModalService } from './create-user-group-modal.service';
import {
  leadingOrTrailingWhitespace,
  multipleWhitespaces,
  unique,
} from './validators';

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Save',
  title: 'Create a new user group',
};

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Description',
  placeholder: 'Please describe the user group...',
  requiredErrorMessage: 'Please provide a description of the user group',
};

@Component({
  selector: 'models4insight-create-user-group-modal',
  templateUrl: 'create-user-group-modal.component.html',
  styleUrls: ['create-user-group-modal.component.scss'],
})
export class CreateUserGroupModalComponent
  extends AbstractModalForm<UserGroup>
  implements OnInit
{
  readonly descriptionContext = descriptionContext;

  suggestions$: Observable<string[]>;

  accessManagementTab: 'members' | 'add' = 'members';
  currentTab: 'general' | 'access' = 'general';
  members: UntypedFormArray;

  faInfo = faInfo;
  faShieldAlt = faShieldAlt;
  faUserCog = faUserCog;
  faUserPlus = faUserPlus;

  private groupNames: string[] = [];

  constructor(
    private readonly createUserGroupModalService: CreateUserGroupModalService,
    private readonly projectUserGroupsService: ProjectUserGroupsService,
    private readonly formBuilder: UntypedFormBuilder
  ) {
    super('user group');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();
    this.modal.context = modalContext;

    // Whenever the form is successfully submitted, create the user group in the back end
    this.submission
      .pipe(untilDestroyed(this))
      .subscribe((userGroup) =>
        this.projectUserGroupsService.updateUserGroup(userGroup)
      );

    // Collect the names of the user groups for form validation
    this.projectUserGroupsService.userGroups
      .pipe(map((userGroups) => userGroups.map((userGroup) => userGroup.name)))
      .subscribe((groupNames) => (this.groupNames = groupNames));
  }

  addMember(name: string) {
    this.members.push(this.formBuilder.control(name));
  }

  protected createSubmission() {
    return this.form.value;
  }

  protected initForm(): UntypedFormGroup {
    this.members = this.formBuilder.array([]);
    return this.formBuilder.group({
      id: this.formBuilder.control(undefined),
      name: this.formBuilder.control('', [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(50),
        leadingOrTrailingWhitespace,
        multipleWhitespaces,
        unique(
          () => this.groupNames,
          () => (this.subject ? this.subject.name : null)
        ),
      ]),
      description: new DescriptionInput(),
      members: this.members,
    });
  }

  protected onSubjectChanged(userGroup: UserGroup) {
    super.onSubjectChanged(userGroup);

    // Reset the current state of the component and the store
    this.members.clear();

    this.createUserGroupModalService.delete({
      description: 'Current group name deleted',
      path: ['currentGroupName'],
    });

    this.createUserGroupModalService.delete({
      description: 'Connected groups deleted',
      path: ['connectedGroups'],
    });

    // If the user group is not null, update the store and add controls for each member
    if (userGroup) {
      this.createUserGroupModalService.update({
        description: 'Current group name updated',
        payload: {
          currentGroupName: userGroup.name,
        },
      });
      // Fall back to an empty array if the members property is not initialized correctly
      (userGroup.members || []).forEach((member) => this.addMember(member));
    }
  }
}
