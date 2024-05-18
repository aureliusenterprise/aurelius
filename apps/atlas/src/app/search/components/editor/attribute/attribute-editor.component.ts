import { Component } from '@angular/core';
import {
  FormControl,
  FormGroup,
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

function createAttributeEditorForm(): UntypedFormGroup {
  const name = new FormControl<string>(null, [Validators.required]),
    typeAlias = new FormControl<string>(null),
    definition = new FormControl<string>(null),
    qualifiedName = new FormControl<string>(null);

  const attributes = new FormGroup({
    name,
    typeAlias,
    definition,
    qualifiedName,
  });

  const classifications = new UntypedFormArray([]);

  const businessOwner = new UntypedFormArray([]),
    dataEntity = new UntypedFormArray([]),
    fields = new UntypedFormArray([]),
    steward = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    businessOwner,
    dataEntity,
    fields,
    steward,
  });

  return new UntypedFormGroup({
    attributes,
    classifications,
    relationshipAttributes,
  });
}

function mergeAttributeEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes, classifications, relationshipAttributes } = form.value;

  merge(entity.attributes, attributes);
  entity.classifications = classifications;
  Object.assign(entity.relationshipAttributes, relationshipAttributes);

  return entityDetails;
}

function updateAttributeEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const classifications: UntypedFormArray = form.get(
    'classifications'
  ) as UntypedFormArray;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const businessOwners: UntypedFormArray = relationshipAttributes.get(
    'businessOwner'
  ) as UntypedFormArray;

  const dataEntity: UntypedFormArray = relationshipAttributes.get(
    'dataEntity'
  ) as UntypedFormArray;

  const fields: UntypedFormArray = relationshipAttributes.get(
    'fields'
  ) as UntypedFormArray;

  const stewards: UntypedFormArray = relationshipAttributes.get(
    'steward'
  ) as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  classifications.clear();
  entityDetails.entity.classifications
    ?.filter(
      (classification) =>
        classification.entityGuid === entityDetails.entity.guid
    )
    .forEach((classification) =>
      classifications.push(new UntypedFormControl(classification))
    );

  businessOwners.clear();
  entityDetails.entity.relationshipAttributes.businessOwner?.forEach((person) =>
    businessOwners.push(new UntypedFormControl(person))
  );

  dataEntity.clear();
  entityDetails.entity.relationshipAttributes.dataEntity?.forEach((entity) =>
    dataEntity.push(new UntypedFormControl(entity))
  );

  fields.clear();
  entityDetails.entity.relationshipAttributes.fields?.forEach((field) =>
    fields.push(new UntypedFormControl(field))
  );

  stewards.clear();
  entityDetails.entity.relationshipAttributes.steward?.forEach((person) =>
    stewards.push(new UntypedFormControl(person))
  );
}

@Component({
  selector: 'models4insight-attribute-editor',
  templateUrl: 'attribute-editor.component.html',
  styleUrls: ['attribute-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createAttributeEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeAttributeEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateAttributeEditorForm },
  ],
})
export class AttributeEditorComponent {
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

  get classifications() {
    return this.editorFormService.form.get('classifications');
  }

  get dataEntities() {
    return this.editorFormService.form.get('relationshipAttributes.dataEntity');
  }

  get dataOwners() {
    return this.editorFormService.form.get(
      'relationshipAttributes.businessOwner'
    );
  }

  get dataStewards() {
    return this.editorFormService.form.get('relationshipAttributes.steward');
  }

  get definition() {
    return this.editorFormService.form.get('attributes.definition');
  }

  get fields() {
    return this.editorFormService.form.get('relationshipAttributes.fields');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
