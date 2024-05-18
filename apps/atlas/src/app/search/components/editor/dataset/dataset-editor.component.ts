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

function createDatasetEditorForm(): UntypedFormGroup {
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

  const fields = new UntypedFormArray([]),
    childDataset = new UntypedFormArray([]),
    collections = new UntypedFormArray([]),
    inputToProcesses = new UntypedFormArray([]),
    outputFromProcesses = new UntypedFormArray([]),
    parentDataset = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    fields,
    childDataset,
    collections,
    inputToProcesses,
    outputFromProcesses,
    parentDataset,
  });

  return new UntypedFormGroup({ attributes, relationshipAttributes });
}

function mergeDatasetEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes, relationshipAttributes } = form.value;

  merge(entity.attributes, attributes);
  Object.assign(entity.relationshipAttributes, relationshipAttributes);

  return entityDetails;
}

function updateDatasetEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const fields: UntypedFormArray = relationshipAttributes.get(
    'fields'
  ) as UntypedFormArray;

  const childDataset: UntypedFormArray = relationshipAttributes.get(
    'childDataset'
  ) as UntypedFormArray;

  const collections: UntypedFormArray = relationshipAttributes.get(
    'collections'
  ) as UntypedFormArray;

  const inputToProcesses: UntypedFormArray = relationshipAttributes.get(
    'inputToProcesses'
  ) as UntypedFormArray;

  const outputFromProcesses: UntypedFormArray = relationshipAttributes.get(
    'outputFromProcesses'
  ) as UntypedFormArray;

  const parentDataset: UntypedFormArray = relationshipAttributes.get(
    'parentDataset'
  ) as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  fields.clear();
  entityDetails.entity.relationshipAttributes.fields?.forEach((field) =>
    fields.push(new UntypedFormControl(field))
  );

  childDataset.clear();
  entityDetails.entity.relationshipAttributes.childDataset?.forEach((dataset) =>
    childDataset.push(new UntypedFormControl(dataset))
  );

  collections.clear();
  entityDetails.entity.relationshipAttributes.collections?.forEach(
    (collection) => collections.push(new UntypedFormControl(collection))
  );

  inputToProcesses.clear();
  entityDetails.entity.relationshipAttributes.inputToProcesses?.forEach(
    (process) => inputToProcesses.push(new UntypedFormControl(process))
  );

  outputFromProcesses.clear();
  entityDetails.entity.relationshipAttributes.outputFromProcesses?.forEach(
    (process) => outputFromProcesses.push(new UntypedFormControl(process))
  );

  parentDataset.clear();
  entityDetails.entity.relationshipAttributes.parentDataset?.forEach(
    (dataset) => parentDataset.push(new UntypedFormControl(dataset))
  );
}

@Component({
  selector: 'models4insight-dataset-editor',
  templateUrl: 'dataset-editor.component.html',
  styleUrls: ['dataset-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createDatasetEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeDatasetEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateDatasetEditorForm },
  ],
})
export class DatasetEditorComponent {
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

  get childDatasets() {
    return this.editorFormService.form.get(
      'relationshipAttributes.childDataset'
    );
  }

  get collections() {
    return this.editorFormService.form.get(
      'relationshipAttributes.collections'
    );
  }

  get definition() {
    return this.editorFormService.form.get('attributes.definition');
  }

  get fields() {
    return this.editorFormService.form.get('relationshipAttributes.fields');
  }

  get inputToProcesses() {
    return this.editorFormService.form.get(
      'relationshipAttributes.inputToProcesses'
    );
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get outputFromProcesses() {
    return this.editorFormService.form.get(
      'relationshipAttributes.outputFromProcesses'
    );
  }

  get parentDatasets() {
    return this.editorFormService.form.get(
      'relationshipAttributes.parentDataset'
    );
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
