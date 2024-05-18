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

function createDomainEditorForm(): UntypedFormGroup {
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

  const dataEntity = new UntypedFormArray([]),
    domainLead = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    dataEntity,
    domainLead,
  });

  return new UntypedFormGroup({
    attributes,
    classifications,
    relationshipAttributes,
  });
}

function mergeDomainEditorForm(
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

function updateDomainEditorForm(
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

  const dataEntities: UntypedFormArray = relationshipAttributes.get(
    'dataEntity'
  ) as UntypedFormArray;

  const domainLeads: UntypedFormArray = relationshipAttributes.get(
    'domainLead'
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

  dataEntities.clear();
  entityDetails.entity.relationshipAttributes.dataEntity?.forEach(
    (dataEntity) => dataEntities.push(new UntypedFormControl(dataEntity))
  );

  domainLeads.clear();
  entityDetails.entity.relationshipAttributes.domainLead?.forEach(
    (domainLead) => domainLeads.push(new UntypedFormControl(domainLead))
  );
}

@Component({
  selector: 'models4insight-domain-editor',
  templateUrl: 'domain-editor.component.html',
  styleUrls: ['domain-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createDomainEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeDomainEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateDomainEditorForm },
  ],
})
export class DomainEditorComponent {
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

  get definition() {
    return this.editorFormService.form.get('attributes.definition');
  }

  get domainLeads() {
    return this.editorFormService.form.get('relationshipAttributes.domainLead');
  }

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get qualifiedName() {
    return this.editorFormService.form.get('attributes.qualifiedName');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
