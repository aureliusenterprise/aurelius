import { Component } from '@angular/core';
import {
  FormControl,
  UntypedFormArray,
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

function createProcessEditorForm(): UntypedFormGroup {
  const name = new FormControl<string>(null, [Validators.required]),
    typeAlias = new FormControl<string>(null),
    definition = new FormControl<string>(null),
    qualifiedName = new FormControl<string>(null);

  const attributes = new UntypedFormGroup({
    definition,
    name,
    qualifiedName,
    typeAlias,
  });

  const inputs = new UntypedFormArray([]),
    outputs = new UntypedFormArray([]),
    system = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    inputs,
    outputs,
    system,
  });

  return new UntypedFormGroup({ attributes, relationshipAttributes });
}

function mergeProcessEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes, relationshipAttributes } = form.value;

  merge(entity.attributes, attributes);
  Object.assign(entity.relationshipAttributes, relationshipAttributes);

  return entityDetails;
}

function updateProcessEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const inputs = relationshipAttributes.get('inputs') as UntypedFormArray,
    outputs = relationshipAttributes.get('outputs') as UntypedFormArray,
    systems = relationshipAttributes.get('system') as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  inputs.clear();
  entityDetails.entity.relationshipAttributes.inputs?.forEach((dataset) =>
    inputs.push(new UntypedFormControl(dataset))
  );

  outputs.clear();
  entityDetails.entity.relationshipAttributes.outputs?.forEach((dataset) =>
    outputs.push(new UntypedFormControl(dataset))
  );

  systems.clear();
  entityDetails.entity.relationshipAttributes.system?.forEach((system) =>
    systems.push(new UntypedFormControl(system))
  );
}

@Component({
  selector: 'models4insight-process-editor',
  templateUrl: 'process-editor.component.html',
  styleUrls: ['process-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createProcessEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeProcessEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateProcessEditorForm },
  ],
})
export class ProcessEditorComponent {
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

  get definition() {
    return this.editorFormService.form.get('attributes.definition');
  }

  get inputs() {
    return this.editorFormService.form.get('relationshipAttributes.inputs');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get outputs() {
    return this.editorFormService.form.get('relationshipAttributes.outputs');
  }

  get systems() {
    return this.editorFormService.form.get('relationshipAttributes.system');
  }
}
