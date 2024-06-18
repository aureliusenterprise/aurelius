import { Component, OnInit } from '@angular/core';
import {
  UntypedFormControl,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { faQuestionCircle } from '@fortawesome/free-solid-svg-icons';
import { AbstractModal, defaultModalContext, ModalContext } from '../../modal';
import { Select } from '../../select';

const commitOptionsModalContext: ModalContext = {
  ...defaultModalContext,
  confirm: null,
  title: 'Commit options',
};

@Component({
  selector: 'models4insight-commit-options-modal',
  templateUrl: 'commit-options-modal.component.html',
  styleUrls: ['commit-options-modal.component.scss'],
})
export class CommitOptionsModalComponent
  extends AbstractModal
  implements OnInit
{
  readonly faQuestionCircle = faQuestionCircle;
  readonly form: UntypedFormGroup;

  constructor() {
    super();

    this.form = new UntypedFormGroup({
      conflictResolutionTemplate: new Select(false),
      keepOriginalIds: new UntypedFormControl(false, Validators.required),
    });
  }

  ngOnInit() {
    if (this.modal.context === defaultModalContext) {
      this.modal.context = commitOptionsModalContext;
    }
  }
}
