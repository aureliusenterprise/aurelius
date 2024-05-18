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

function createPersonEditorForm(): UntypedFormGroup {
  const email = new UntypedFormControl(null, [
      Validators.required,
      Validators.email,
    ]),
    name = new UntypedFormControl(null, [Validators.required]),
    typeAlias = new FormControl<string>(null),
    qualifiedName = new UntypedFormControl(null);

  const attributes = new UntypedFormGroup({
    email,
    name,
    qualifiedName,
    typeAlias,
  });

  const businessOwnerAttribute = new UntypedFormArray([]),
    businessOwnerEntity = new UntypedFormArray([]),
    domainLead = new UntypedFormArray([]),
    stewardAttribute = new UntypedFormArray([]),
    stewardEntity = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    businessOwnerAttribute,
    businessOwnerEntity,
    domainLead,
    stewardAttribute,
    stewardEntity,
  });

  return new UntypedFormGroup({ attributes, relationshipAttributes });
}

function mergePersonEditorForm(
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

  const businessOwnerAttribute = relationshipAttributes.get(
    'businessOwnerAttribute'
  ) as UntypedFormArray;

  const businessOwnerEntity = relationshipAttributes.get(
    'businessOwnerEntity'
  ) as UntypedFormArray;

  const domainLead = relationshipAttributes.get(
    'domainLead'
  ) as UntypedFormArray;

  const stewardAttribute = relationshipAttributes.get(
    'stewardAttribute'
  ) as UntypedFormArray;

  const stewardEntity = relationshipAttributes.get(
    'stewardEntity'
  ) as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  businessOwnerAttribute.clear();
  entityDetails.entity.relationshipAttributes.businessOwnerAttribute?.forEach(
    (attribute) =>
      businessOwnerAttribute.push(new UntypedFormControl(attribute))
  );

  businessOwnerEntity.clear();
  entityDetails.entity.relationshipAttributes.businessOwnerEntity?.forEach(
    (entity) => businessOwnerEntity.push(new UntypedFormControl(entity))
  );

  domainLead.clear();
  entityDetails.entity.relationshipAttributes.domainLead?.forEach((domain) =>
    domainLead.push(new UntypedFormControl(domain))
  );

  stewardAttribute.clear();
  entityDetails.entity.relationshipAttributes.stewardAttribute?.forEach(
    (attribute) => stewardAttribute.push(new UntypedFormControl(attribute))
  );

  stewardEntity.clear();
  entityDetails.entity.relationshipAttributes.stewardEntity?.forEach((entity) =>
    stewardEntity.push(new UntypedFormControl(entity))
  );
}

@Component({
  selector: 'models4insight-person-editor',
  templateUrl: 'person-editor.component.html',
  styleUrls: ['person-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createPersonEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergePersonEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateProcessEditorForm },
  ],
})
export class PersonEditorComponent {
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

  get businessOwnerAttributes() {
    return this.editorFormService.form.get(
      'relationshipAttributes.businessOwnerAttribute'
    );
  }

  get businessOwnerEntities() {
    return this.editorFormService.form.get(
      'relationshipAttributes.businessOwnerEntity'
    );
  }

  get domainLead() {
    return this.editorFormService.form.get('relationshipAttributes.domainLead');
  }

  get email() {
    return this.editorFormService.form.get('attributes.email');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get qualifiedName() {
    return this.editorFormService.form.get('attributes.qualifiedName');
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get stewardAttributes() {
    return this.editorFormService.form.get(
      'relationshipAttributes.stewardAttribute'
    );
  }

  get stewardEntities() {
    return this.editorFormService.form.get(
      'relationshipAttributes.stewardEntity'
    );
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
