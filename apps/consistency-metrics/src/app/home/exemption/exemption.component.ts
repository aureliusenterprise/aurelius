import { Component } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { AbstractModalForm, BranchSelect, DescriptionInput, ProjectSelect, ProvenanceSelect } from '@models4insight/components';
import { MetricExemption } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { ExemptionService } from './exemption.service';

@Component({
  selector: 'models4insight-exemption',
  templateUrl: 'exemption.component.html',
  styleUrls: ['exemption.component.scss'],
  providers: [ExemptionService]
})
export class ExemptionComponent extends AbstractModalForm<MetricExemption> {
  constructor(private readonly exemptionService: ExemptionService) {
    super('Exemption');
    this.form = this.initForm();
  }

  createSubmission() {
    const { value } = this.form;
    return {
      id: value.id,
      branch_id: value.branch.id,
      comment: value.comment,
      concept_id: value.concept_id,
      metric: value.metric,
      project_id: value.project.id,
      version: value.version.start_time
    };
  }

  initForm() {
    const projectSelect = new ProjectSelect(),
      branchSelect = new BranchSelect(),
      versionSelect = new ProvenanceSelect();

    projectSelect.valueChanges.pipe(untilDestroyed(this)).subscribe(project => {
      this.exemptionService.loadBranches(project);
      branchSelect.reset();
      versionSelect.reset();
    });

    branchSelect.valueChanges.pipe(untilDestroyed(this)).subscribe(branch => {
      this.exemptionService.loadVersions(projectSelect.value, branch);
      versionSelect.reset();
    });

    return new UntypedFormGroup({
      branch: branchSelect,
      comment: new DescriptionInput(),
      concept_id: new UntypedFormControl(null, Validators.required),
      id: new UntypedFormControl(),
      metric: new UntypedFormControl(null, Validators.required),
      project: projectSelect,
      version: versionSelect
    });
  }
}
