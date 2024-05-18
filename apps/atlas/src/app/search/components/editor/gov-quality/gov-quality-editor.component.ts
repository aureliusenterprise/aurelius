import { Component } from '@angular/core';
import {
  UntypedFormControl,
  UntypedFormGroup,
  Validators
} from '@angular/forms';
import {
  AtlasEntityWithEXTInformation,
  EntityValidationResponse
} from '@models4insight/atlas/api';
import { merge } from 'lodash';
import { Observable } from 'rxjs';
import {
  EditorFormService,
  EDITOR_FORM_FACTORY,
  EDITOR_MERGE_STRATEGY,
  EDITOR_UPDATE_STRATEGY
} from '../services/editor-form.service';
import { EntityValidateService } from '../services/entity-validate/entity-validate.service';

function createGovQualityEditorForm(): UntypedFormGroup {
  const compliantMessage = new UntypedFormControl(null),
    description = new UntypedFormControl(null),
    expression = new UntypedFormControl(null, [Validators.required]),
    name = new UntypedFormControl(null, [Validators.required]),
    nonCompliantMessage = new UntypedFormControl(null),
    qualifiedName = new UntypedFormControl(null),
    qualityDimension = new UntypedFormControl(null),
    ruleType = new UntypedFormControl(null);

  const attributes = new UntypedFormGroup({
    compliantMessage,
    description,
    expression,
    name,
    nonCompliantMessage,
    qualifiedName,
    qualityDimension,
    ruleType,
  });

  return new UntypedFormGroup({ attributes });
}

function mergeGovQualityEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes } = form.value;

  merge(entity.attributes, attributes);

  return entityDetails;
}

function updateGovQualityEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  attributes.patchValue(entityDetails.entity.attributes);
}

@Component({
  selector: 'models4insight-qov-quality-editor',
  templateUrl: 'gov-quality-editor.component.html',
  styleUrls: ['gov-quality-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createGovQualityEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeGovQualityEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateGovQualityEditorForm },
  ],
})
export class GovernanceQualityEditorComponent {
  readonly validationResults$: Observable<EntityValidationResponse>;

  constructor(
    readonly editorFormService: EditorFormService,
    private readonly entityValidateService: EntityValidateService
  ) {
    this.validationResults$ = this.entityValidateService.validationResults$;
  }

  get attributes() {
    return this.editorFormService.form.get('attributes');
  }

  get compliantMessage() {
    return this.editorFormService.form.get('attributes.compliantMessage');
  }

  get description() {
    return this.editorFormService.form.get('attributes.description');
  }

  get expression() {
    return this.editorFormService.form.get('attributes.expression');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get nonCompliantMessage() {
    return this.editorFormService.form.get('attributes.nonCompliantMessage');
  }

  get qualityDimension() {
    return this.editorFormService.form.get('attributes.qualityDimension');
  }

  get ruleType() {
    return this.editorFormService.form.get('attributes.ruleType');
  }
}
