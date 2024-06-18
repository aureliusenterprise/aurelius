import { Component, OnInit } from '@angular/core';
import {
  UntypedFormControl,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { Branch, ModelProvenance } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AbstractModalForm } from '../abstract-modal-form';
import { defaultModalContext, ModalContext } from '../modal';
import { Select } from '../select';
import { CompareModalService } from './compare-modal.service';

export interface ComparisonContext {
  baseBranch: string;
  otherBranch: string;
  baseVersion?: number;
  otherVersion?: number;
}

const modalContext: ModalContext = {
  ...defaultModalContext,
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Compare',
  title: 'Compare model versions',
};

@Component({
  selector: 'models4insight-compare-modal',
  templateUrl: './compare-modal.component.html',
  styleUrls: ['./compare-modal.component.scss'],
  providers: [CompareModalService],
})
export class CompareModalComponent
  extends AbstractModalForm<ComparisonContext>
  implements OnInit
{
  versions$: Observable<ModelProvenance[]>;

  constructor(private readonly compareModalService: CompareModalService) {
    super('model comparison');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();

    if (this.modal.context === defaultModalContext) {
      this.modal.context = modalContext;
    }

    this.versions$ = this.compareModalService.versions;
  }

  activateAndPrefill(branchName: string, version: number) {
    this.form.patchValue({
      baseBranch: branchName,
      baseVersion: version,
    });
    this.activate();
  }

  createSubmission() {
    const { baseBranch, otherBranch, baseVersion, otherVersion } =
      this.form.value;

    return {
      baseBranch,
      baseVersion,
      otherBranch: otherBranch.name,
      otherVersion: otherVersion?.start_date,
    };
  }

  initForm() {
    const otherBranch = new Select(true),
      otherVersion = new Select();

    // Whenever a new other branch is selected, retrieve the model versions for that branch
    otherBranch.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((branch) => this.compareModalService.loadVersions(branch));

    // Whenever new model versions become available, reset the other version select
    this.compareModalService.versions
      .pipe(untilDestroyed(this))
      .subscribe(() => otherVersion.reset());

    return new UntypedFormGroup({
      baseBranch: new UntypedFormControl(null, Validators.required),
      otherBranch,
      baseVersion: new UntypedFormControl(null),
      otherVersion,
    });
  }
}
