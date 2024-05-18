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

function createSystemEditorForm(): UntypedFormGroup {
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

  const childSystem = new UntypedFormArray([]),
    collections = new UntypedFormArray([]),
    parentSystem = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({
    childSystem,
    collections,
    parentSystem,
  });

  return new UntypedFormGroup({ attributes, relationshipAttributes });
}

function mergeSystemEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
): AtlasEntityWithEXTInformation {
  const entity = entityDetails.entity,
    { attributes, relationshipAttributes } = form.value;

  merge(entity.attributes, attributes);
  Object.assign(entity.relationshipAttributes, relationshipAttributes);

  return entityDetails;
}

function updateSystemEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const childSystem = relationshipAttributes.get(
    'childSystem'
  ) as UntypedFormArray;

  const collections = relationshipAttributes.get(
    'collections'
  ) as UntypedFormArray;

  const parentSystem = relationshipAttributes.get(
    'parentSystem'
  ) as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  childSystem.clear();
  entityDetails.entity.relationshipAttributes.childSystem?.forEach((system) =>
    childSystem.push(new UntypedFormControl(system))
  );

  collections.clear();
  entityDetails.entity.relationshipAttributes.collections?.forEach(
    (collection) => collections.push(new UntypedFormControl(collection))
  );

  parentSystem.clear();
  entityDetails.entity.relationshipAttributes.parentSystem?.forEach((system) =>
    parentSystem.push(new UntypedFormControl(system))
  );
}

@Component({
  selector: 'models4insight-system-editor',
  templateUrl: 'system-editor.component.html',
  styleUrls: ['system-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createSystemEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeSystemEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateSystemEditorForm },
  ],
})
export class SystemEditorComponent {
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

  get childSystems() {
    return this.editorFormService.form.get(
      'relationshipAttributes.childSystem'
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

  get name() {
    return this.editorFormService.form.get('attributes.name');
  }

  get qualifiedName() {
    return this.editorFormService.form.get('attributes.qualifiedName');
  }

  get parentSystems() {
    return this.editorFormService.form.get(
      'relationshipAttributes.parentSystem'
    );
  }

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
