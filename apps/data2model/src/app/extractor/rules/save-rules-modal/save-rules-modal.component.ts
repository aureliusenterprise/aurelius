import { Component, OnInit } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { AbstractModalForm, ModalContext } from '@models4insight/components';
import { saveAsFile, untilDestroyed } from '@models4insight/utils';
import { ExtractorService } from '../../extractor.service';

const modalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: false,
  confirm: 'Save',
  title: 'Save extractor rules'
};

@Component({
  selector: 'models4insight-save-rules-modal',
  templateUrl: 'save-rules-modal.component.html',
  styleUrls: ['save-rules-modal.component.scss']
})
export class SaveRulesModalComponent extends AbstractModalForm<string>
  implements OnInit {
  readonly modalContext = modalContext;

  constructor(private readonly extractorService: ExtractorService) {
    super('Ruleset');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();

    // Make sure the form value is consistent with the peristed ruleset name
    this.extractorService
      .select(['rulesContext', 'name'], { includeFalsy: true })
      .pipe(untilDestroyed(this))
      .subscribe(name => this.form.patchValue({ name }, { emitEvent: false }));

    // Whenever the current name changes, persist the value
    this.form.controls.name.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe(name =>
        this.extractorService.update({
          description: 'New rules name available',
          path: ['rulesContext', 'name'],
          payload: name
        })
      );

    // Whenever the form is submitted, download the current ruleset
    this.submission
      .pipe(untilDestroyed(this))
      .subscribe(() => this.saveRules());
  }

  createSubmission() {
    return this.form.value.name;
  }

  initForm() {
    return new UntypedFormGroup({
      name: new UntypedFormControl('', Validators.required)
    });
  }

  private async saveRules() {
    const [rules, fileName] = await Promise.all([
      this.extractorService.get(['rulesContext']),
      this.extractorService.get('currentRulesFileName')
    ]);

    saveAsFile(JSON.stringify(rules), fileName);
  }
}
