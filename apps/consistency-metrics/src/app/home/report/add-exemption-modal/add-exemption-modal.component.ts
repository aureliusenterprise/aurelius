import { Component, Input, OnInit } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { AbstractModalForm, DescriptionInput, ModalContext, Select } from '@models4insight/components';
import { ExemptionScope } from '../report.service';

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Save',
  title: 'Create a new exemption'
};

export interface AddExemptionModalFormContext {
  readonly id?: string;
  readonly conceptId?: string;
  readonly comment?: string;
  readonly scope?: ExemptionScope;
}

@Component({
  selector: 'models4insight-add-exemption-modal',
  templateUrl: 'add-exemption-modal.component.html',
  styleUrls: ['add-exemption-modal.component.scss']
})
export class AddExemptionModalComponent
  extends AbstractModalForm<AddExemptionModalFormContext>
  implements OnInit {
  constructor() {
    super('exemption');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();
    this.modal.context = modalContext;
  }

  createSubmission() {
    const { id, conceptId, scope, comment } = this.form.value;
    return { id, conceptId, comment, scope: scope.type };
  }

  initForm() {
    return new UntypedFormGroup({
      id: new UntypedFormControl(null),
      conceptId: new UntypedFormControl(null, Validators.required),
      scope: new Select(true),
      comment: new DescriptionInput()
    });
  }

  @Input() set conceptId(conceptId: string) {
    this.form.reset({ conceptId });
  }

  get conceptId(): string {
    return this.form.value.conceptId;
  }
}
