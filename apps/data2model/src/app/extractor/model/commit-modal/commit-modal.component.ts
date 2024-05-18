import { Component } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { faSync } from '@fortawesome/free-solid-svg-icons';
import { AbstractModalForm, BranchSelect, ModalContext, ProjectSelect } from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { ModelCommitContext } from '../../extractor-types';

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Save',
  title: 'Save the model to the repository'
};

@Component({
  selector: 'models4insight-commit-modal',
  templateUrl: 'commit-modal.component.html',
  styleUrls: ['commit-modal.component.scss']
})
export class CommitModalComponent extends AbstractModalForm<
  ModelCommitContext
> {
  readonly faSync = faSync;
  readonly modalContext = modalContext;

  constructor() {
    super('Save the model to the repository');
    this.form = this.initForm();
  }

  createSubmission() {
    const { value } = this.form;
    return {
      ...value,
      projectName: value.projectName.project,
      branchName: value.branchName.name,
      conflictResolutionTemplate: value.conflictResolutionTemplate.template
    };
  }

  initForm() {
    const projectName = new ProjectSelect();
    const branchName = new BranchSelect();

    // Whenever the selected project changes, update the list of branch names and reset the branch selection
    projectName.valueChanges.pipe(untilDestroyed(this)).subscribe(() => {
      branchName.reset();
    });

    return new UntypedFormGroup({
      projectName,
      branchName,
      conflictResolutionTemplate: new UntypedFormControl(null, [Validators.required]),
      comment: new UntypedFormControl('', [Validators.required])
    });
  }
}
