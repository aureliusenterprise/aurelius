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

function createFieldEditorForm(): UntypedFormGroup {
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

  const childField = new UntypedFormArray([]),
    dataAttributes = new UntypedFormArray([]),
    datasets = new UntypedFormArray([]),
    parentField = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    attributes: dataAttributes,
    childField,
    datasets,
    parentField,
  });

  return new UntypedFormGroup({ attributes, relationshipAttributes });
}

function mergeFieldEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes, relationshipAttributes } = form.value;

  merge(entity.attributes, attributes);
  Object.assign(entity.relationshipAttributes, relationshipAttributes);

  return entityDetails;
}

function updateFieldEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const childField: UntypedFormArray = relationshipAttributes.get(
    'childField'
  ) as UntypedFormArray;

  const dataAttributes: UntypedFormArray = relationshipAttributes.get(
    'attributes'
  ) as UntypedFormArray;

  const datasets: UntypedFormArray = relationshipAttributes.get(
    'datasets'
  ) as UntypedFormArray;

  const parentField: UntypedFormArray = relationshipAttributes.get(
    'parentField'
  ) as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  childField.clear();
  entityDetails.entity.relationshipAttributes.childField?.forEach((field) =>
    childField.push(new UntypedFormControl(field))
  );

  dataAttributes.clear();
  entityDetails.entity.relationshipAttributes.attributes?.forEach((attribute) =>
    dataAttributes.push(new UntypedFormControl(attribute))
  );

  datasets.clear();
  entityDetails.entity.relationshipAttributes.datasets?.forEach((dataset) =>
    datasets.push(new UntypedFormControl(dataset))
  );

  parentField.clear();
  entityDetails.entity.relationshipAttributes.parentField?.forEach((field) =>
    parentField.push(new UntypedFormControl(field))
  );
}

@Component({
  selector: 'models4insight-field-editor',
  templateUrl: 'field-editor.component.html',
  styleUrls: ['field-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createFieldEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeFieldEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateFieldEditorForm },
  ],
})
export class FieldEditorComponent {
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

  get childFields() {
    return this.editorFormService.form.get('relationshipAttributes.childField');
  }

  get dataAttributes() {
    return this.editorFormService.form.get('relationshipAttributes.attributes');
  }

  get datasets() {
    return this.editorFormService.form.get('relationshipAttributes.datasets');
  }

  get definition() {
    return this.editorFormService.form.get('attributes.definition');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get parentFields() {
    return this.editorFormService.form.get(
      'relationshipAttributes.parentField'
    );
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
