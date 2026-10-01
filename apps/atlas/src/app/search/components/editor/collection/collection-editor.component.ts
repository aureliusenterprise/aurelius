import { Component } from '@angular/core';
import {
  FormControl,
  UntypedFormArray,
  UntypedFormControl,
  UntypedFormGroup,
  ValidationErrors,
  ValidatorFn,
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

function rightSingleQuotationMarkValidator(): ValidatorFn {
  return (control): ValidationErrors | null => {
    if (!control.value) {
      return null;
    }
    // Check for right single quotation mark (U+2019)
    const hasRightSingleQuotation = /[’]/.test(control.value);
    return hasRightSingleQuotation ? { rightSingleQuotationMark: true } : null;
  };
}

function createCollectionEditorForm(): UntypedFormGroup {
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

  const datasets = new UntypedFormArray([]),
    systems = new UntypedFormArray([]);

  const relationshipAttributes = new UntypedFormGroup({ datasets, systems });

  const classifications = new UntypedFormArray([]);

  return new UntypedFormGroup({ attributes, classifications, relationshipAttributes });
}

function mergeCollectionEditorForm(
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

function updateCollectionEditorForm(
  entityDetails: AtlasEntityWithEXTInformation,
  form: UntypedFormGroup
) {
  const attributes: UntypedFormGroup = form.get(
    'attributes'
  ) as UntypedFormGroup;

  const relationshipAttributes: UntypedFormGroup = form.get(
    'relationshipAttributes'
  ) as UntypedFormGroup;

  const datasets = relationshipAttributes.get('datasets') as UntypedFormArray;

  const systems = relationshipAttributes.get('systems') as UntypedFormArray;

  attributes.patchValue(entityDetails.entity.attributes);

  // the entity's own classifications (propagated ones are shown on the details page, not edited here)
  const classifications = form.get('classifications') as UntypedFormArray;
  classifications.clear();
  (entityDetails.entity.classifications ?? [])
    .filter((classification) => classification.entityGuid === entityDetails.entity.guid)
    .forEach((classification) => classifications.push(new UntypedFormControl(classification)));

  datasets.clear();
  entityDetails.entity.relationshipAttributes.datasets?.forEach((dataset) =>
    datasets.push(new UntypedFormControl(dataset))
  );

  systems.clear();
  entityDetails.entity.relationshipAttributes.systems?.forEach((system) =>
    systems.push(new UntypedFormControl(system))
  );
}

@Component({
  selector: 'models4insight-collection-editor',
  templateUrl: 'collection-editor.component.html',
  styleUrls: ['collection-editor.component.scss'],
  providers: [
    EditorFormService,
    EntityValidateService,
    { provide: EDITOR_FORM_FACTORY, useValue: createCollectionEditorForm },
    { provide: EDITOR_MERGE_STRATEGY, useValue: mergeCollectionEditorForm },
    { provide: EDITOR_UPDATE_STRATEGY, useValue: updateCollectionEditorForm },
  ],
})
export class CollectionEditorComponent {
  readonly validationResults$: Observable<EntityValidationResponse>;

  constructor(
    readonly editorFormService: EditorFormService,
    private readonly entityValidateService: EntityValidateService
  ) {
    this.validationResults$ = this.entityValidateService.validationResults$;
  }

  get classifications() {
    return this.editorFormService.form.get('classifications') as UntypedFormArray;
  }

  get attributes() {
    return this.editorFormService.form.get('attributes');
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

  get relationshipAttributes() {
    return this.editorFormService.form.get('relationshipAttributes');
  }

  get systems() {
    return this.editorFormService.form.get('relationshipAttributes.systems');
  }

  get typeAlias() {
    return this.editorFormService.form.get('attributes.typeAlias');
  }
}
