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

function createEntityEditorForm(): UntypedFormGroup {
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

  const classifications = new UntypedFormArray([]);

  const businessOwner = new UntypedFormArray([]),
    childEntity = new UntypedFormArray([]),
    dataAttributes = new UntypedFormArray([]),
    dataDomain = new UntypedFormArray([]),
    parentEntity = new UntypedFormArray([]),
    steward = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    attributes: dataAttributes,
    businessOwner,
    childEntity,
    dataDomain,
    parentEntity,
    steward,
  });

  return new UntypedFormGroup({
    attributes,
    classifications,
    relationshipAttributes,
  });
}

function mergeEntityEditorForm(
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

function updateEntityEditorForm(
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

  const childEntities: UntypedFormArray = relationshipAttributes.get(
    'childEntity'
  ) as UntypedFormArray;

  const dataAttributes: UntypedFormArray = relationshipAttributes.get(
    'attributes'
  ) as UntypedFormArray;

  const dataDomain: UntypedFormArray = relationshipAttributes.get(
    'dataDomain'
  ) as UntypedFormArray;

  const parentEntity: UntypedFormArray = relationshipAttributes.get(
    'parentEntity'
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

  childEntities.clear();
  entityDetails.entity.relationshipAttributes.childEntity?.forEach(
    (dataEntity) => childEntities.push(new UntypedFormControl(dataEntity))
  );

  dataAttributes.clear();
  entityDetails.entity.relationshipAttributes.attributes?.forEach((attribute) =>
    dataAttributes.push(new UntypedFormControl(attribute))
  );

  dataDomain.clear();
  entityDetails.entity.relationshipAttributes.dataDomain?.forEach((domain) =>
    dataDomain.push(new UntypedFormControl(domain))
  );

  parentEntity.clear();
  entityDetails.entity.relationshipAttributes.parentEntity?.forEach(
    (dataEntity) => parentEntity.push(new UntypedFormControl(dataEntity))
  );

  stewards.clear();
  entityDetails.entity.relationshipAttributes.steward?.forEach((person) =>
    stewards.push(new UntypedFormControl(person))
  );
}
@Component({
  selector: 'models4insight-entity-editor',
  templateUrl: 'entity-editor.component.html',
  styleUrls: ['entity-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createEntityEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeEntityEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateEntityEditorForm },
  ],
})
export class EntityEditorComponent {
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

  get childEntities() {
    return this.editorFormService.form.get(
      'relationshipAttributes.childEntity'
    );
  }

  get classifications() {
    return this.editorFormService.form.get('classifications');
  }

  get dataAttributes() {
    return this.editorFormService.form.get('relationshipAttributes.attributes');
  }

  get dataDomains() {
    return this.editorFormService.form.get('relationshipAttributes.dataDomain');
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

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get parentEntities() {
    return this.editorFormService.form.get(
      'relationshipAttributes.parentEntity'
    );
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
