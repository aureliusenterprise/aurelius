import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup } from '@angular/forms';
import {
  faInfo,
  faShieldAlt,
  faUserPlus,
  faUsersCog,
} from '@fortawesome/free-solid-svg-icons';
import {
  Branch,
  BranchPermissionLevel,
  PermissionLevel,
} from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AbstractModalForm } from '../abstract-modal-form/abstract-modal-form';
import { BranchNameInput } from '../branch-name-input';
import {
  defaultDescriptionInputContext,
  DescriptionInput,
  DescriptionInputContext,
} from '../description-input';
import { ModalContext } from '../modal/modal.component';

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Description',
  placeholder: 'Please describe your branch...',
  requiredErrorMessage: 'Please provide a description of your branch',
};

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Save',
  title: 'Create a new branch',
};

@Component({
  selector: 'models4insight-create-branch-modal',
  templateUrl: 'create-branch-modal.component.html',
  styleUrls: ['create-branch-modal.component.scss'],
})
export class CreateBranchModalComponent
  extends AbstractModalForm<Branch>
  implements OnInit, OnDestroy
{
  readonly descriptionContext = descriptionContext;

  faInfo = faInfo;
  faShieldAlt = faShieldAlt;
  faUsersCog = faUsersCog;
  faUsersPlus = faUserPlus;

  currentTab: 'general' | 'access' = 'general';
  accessManagementTab: 'add' | 'members' = 'members';

  members: UntypedFormGroup;

  constructor(
    private readonly branchesService: BranchesService,
    private readonly formBuilder: UntypedFormBuilder
  ) {
    super('branch');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();
    this.modal.context = modalContext;

    // Whenever the form is successfully submitted, save the branch
    this.submission
      .pipe(untilDestroyed(this))
      .subscribe((branch) => this.branchesService.updateBranch(branch));
  }

  ngOnDestroy() {}

  addMember(
    username: string,
    permissionLevel: BranchPermissionLevel = PermissionLevel.BUSINESS_USER
  ) {
    this.members.addControl(
      username,
      this.formBuilder.control(permissionLevel)
    );
  }

  removeMember(username: string) {
    this.members.removeControl(username);
  }

  protected createSubmission(): Branch {
    return this.form.value;
  }

  protected initForm(): UntypedFormGroup {
    this.members = this.formBuilder.group({});

    this.defaultValue = {
      protected: false,
    };

    const branches$ = this.branchesService.branches.pipe(
      map((branches) => branches.map((branch) => branch.name))
    );

    return this.formBuilder.group({
      id: this.formBuilder.control(null),
      name: new BranchNameInput(
        () => branches$,
        () => (this.subject ? this.subject.name : null)
      ),
      description: new DescriptionInput(),
      protected: this.formBuilder.control(false),
      members: this.members,
    });
  }

  protected onSubjectChanged(branch: Branch) {
    super.onSubjectChanged(branch);
    // Remove all member controls and add new ones for the current members
    Object.keys(this.members.controls).forEach((username) =>
      this.removeMember(username)
    );
    if (branch) {
      const members = branch.members || {};
      Object.entries(members).forEach(([username, permissionLevel]) =>
        this.addMember(username, permissionLevel)
      );
    }
  }
}
