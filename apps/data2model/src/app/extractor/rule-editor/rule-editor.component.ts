import { AfterViewInit, Component, OnInit } from '@angular/core';
import { AbstractControl, UntypedFormArray, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { archimate3, toHumanReadableNames } from '@models4insight/metamodel';
import * as bulmaQuickview from 'bulma-quickview/dist/js/bulma-quickview.min.js';
import { EMPTY, Observable, of, Subject } from 'rxjs';
import { shareReplay, switchMap, withLatestFrom } from 'rxjs/operators';
import { DefinitionType, ElementDefinition, RelationshipDefinition, SaveAction, ViewDefinition, ViewLayout } from '../extractor-types';
import { ExtractorService } from '../extractor.service';

function typeIsKnown(control: AbstractControl) {
  if (control.value === 'ar3_Unknown') {
    return { typeUnknown: true };
  }
  return null;
}

@Component({
  selector: 'models4insight-rule-editor',
  templateUrl: 'rule-editor.component.html',
  styleUrls: ['rule-editor.component.scss']
})
export class RuleEditorComponent implements OnInit, AfterViewInit {
  readonly DefinitionType = DefinitionType;
  readonly elementTypes = Object.entries(
    toHumanReadableNames(archimate3.elements)
  );
  readonly relationTypes = Object.entries(
    toHumanReadableNames(archimate3.relations)
  );
  readonly viewLayouts = Object.entries({
    [ViewLayout.ARCHIMATE_HIERARCHICAL]: 'Hierarchical (ArchiMate)',
    [ViewLayout.ARCHIMATE_PROCESS]: 'Process (ArchiMate)'
  });

  currentDefinitionType$: Observable<DefinitionType>;
  headers$: Observable<string[]>;
  isQuickviewActive$: Observable<boolean>;
  isUpdatingRules$: Observable<boolean>;
  elementRules$: Observable<ElementDefinition[]>;
  relationRules$: Observable<RelationshipDefinition[]>;

  elementForm: UntypedFormGroup;
  relationForm: UntypedFormGroup;
  viewForm: UntypedFormGroup;
  isSubmitted: boolean;

  private readonly clearRule$: Subject<void> = new Subject<void>();
  private readonly deleteRule$: Subject<void> = new Subject<void>();
  private readonly saveRule$: Subject<SaveAction> = new Subject<SaveAction>();

  constructor(
    private extractorService: ExtractorService,
    private formBuilder: UntypedFormBuilder
  ) {
    this.initForms();
  }

  ngOnInit() {
    this.currentDefinitionType$ = this.extractorService.select(
      'currentDefinitionType'
    );
    this.headers$ = this.extractorService
      .select('currentHeaders')
      .pipe(shareReplay());
    this.elementRules$ = this.extractorService.elementRules.pipe(shareReplay());
    this.relationRules$ = this.extractorService.relationRules.pipe(
      shareReplay()
    );
    this.isQuickviewActive$ = this.extractorService.select('isQuickviewActive');
    this.isUpdatingRules$ = this.extractorService.select('isUpdatingRules');

    // Whenever a rule is selected, patch the corresponding form.
    this.extractorService.onRuleSelected.subscribe(rule => {
      switch (rule.type) {
        case DefinitionType.ELEMENT:
          this.patchElementForm(rule);
          break;
        case DefinitionType.RELATION:
          this.patchRelationForm(rule);
          break;
        case DefinitionType.VIEW:
          this.patchViewForm(rule);
          break;
      }
    });

    // Whenever the list of rules corresponding to one of the forms changes, reset that form
    this.extractorService.elementRules.subscribe(() => this.resetElementForm());
    this.extractorService.relationRules.subscribe(() =>
      this.resetRelationForm()
    );
    this.extractorService.viewRules.subscribe(() => this.resetViewForm());

    // Whenever a form clear is triggered, reset that form
    this.clearRule$
      .pipe(
        withLatestFrom(this.extractorService.select('currentDefinitionType'))
      )
      .subscribe(([, definitionType]) => {
        switch (definitionType) {
          case DefinitionType.ELEMENT:
            this.resetElementForm();
            break;
          case DefinitionType.RELATION:
            this.resetRelationForm();
            break;
          case DefinitionType.VIEW:
            this.resetViewForm();
            break;
        }
      });

    // Whenever a save is triggered, save the rule from the appropriate form
    this.saveRule$
      .pipe(
        withLatestFrom(this.extractorService.select('currentDefinitionType')),
        switchMap(([action, definitionType]) => {
          this.isSubmitted = true;
          const form = this.getFormForType(definitionType);
          if (this.validateForm(form)) {
            this.isSubmitted = false;
            switch (action) {
              case SaveAction.SAVE:
                return of(Object.assign(form.value, { type: definitionType }));
              case SaveAction.SAVE_AS:
                return of(
                  Object.assign(form.value, { id: null, type: definitionType })
                );
            }
          } else {
            return EMPTY;
          }
        })
      )
      .subscribe(rule => this.extractorService.saveRule(rule));

    // Whenever a delete is triggered, delete the rule and reset the corresponding form
    this.deleteRule$
      .pipe(
        withLatestFrom(this.extractorService.select('currentDefinitionType'))
      )
      .subscribe(([, definitionType]) => {
        const form = this.getFormForType(definitionType);
        this.extractorService.deleteRule(
          Object.assign(form.value, { type: definitionType })
        );
        form.reset({ include: true, id_type: 'dynamic' });
      });
  }

  ngAfterViewInit() {
    // Initialize the quickview component
    bulmaQuickview.attach();
  }

  clearRule() {
    this.clearRule$.next();
  }

  deleteRule(event: boolean) {
    if (event) {
      this.deleteRule$.next();
    }
  }

  saveRule() {
    this.saveRule$.next(SaveAction.SAVE);
  }

  saveRuleAs() {
    this.saveRule$.next(SaveAction.SAVE_AS);
  }

  addElementControl() {
    (this.viewForm.controls.view_nodes as UntypedFormArray).push(
      this.formBuilder.group({
        rule: this.formBuilder.control(null, Validators.required)
      })
    );
  }

  removeElementControl(index: number) {
    (this.viewForm.controls.view_nodes as UntypedFormArray).removeAt(index);
  }

  addEdgeControl() {
    (this.viewForm.controls.view_edges as UntypedFormArray).push(
      this.formBuilder.group({
        rule: this.formBuilder.control(null, Validators.required)
      })
    );
  }

  removeEdgeControl(index: number) {
    (this.viewForm.controls.view_edges as UntypedFormArray).removeAt(index);
  }

  addMappingControl(form: UntypedFormGroup) {
    (form.controls.mapping as UntypedFormArray).push(
      this.formBuilder.group({
        key: this.formBuilder.control('', Validators.required),
        value: this.formBuilder.control(null, Validators.required)
      })
    );
  }

  removeMappingControl(form: UntypedFormGroup, index: number) {
    (form.controls.mapping as UntypedFormArray).removeAt(index);
  }

  addPathControl() {
    (this.viewForm.controls.view_path as UntypedFormArray).push(
      this.formBuilder.group({
        type: this.formBuilder.control('static', Validators.required),
        value: this.formBuilder.control('', Validators.required),
        prefix: this.formBuilder.control('')
      })
    );
  }

  removePathControl(index: number) {
    (this.viewForm.controls.view_path as UntypedFormArray).removeAt(index);
  }

  onViewNameTypeChanged() {
    this.viewForm.controls.view_name_key.reset();
    this.viewForm.controls.view_name_prefix.reset();
    this.viewForm.controls.view_name_value.reset();
  }

  onPathTypeChanged(path: UntypedFormGroup) {
    path.controls.value.reset();
    path.controls.prefix.reset();
  }

  trackByFn(index: number, item: any) {
    return index;
  }

  private getFormForType(type: DefinitionType) {
    switch (type) {
      case DefinitionType.ELEMENT:
        return this.elementForm;
      case DefinitionType.RELATION:
        return this.relationForm;
      case DefinitionType.VIEW:
        return this.viewForm;
    }
  }

  private initForms() {
    this.elementForm = this.formBuilder.group({
      id: this.formBuilder.control(''),
      alias: this.formBuilder.control('', Validators.required),
      description: this.formBuilder.control(''),
      concept_type: this.formBuilder.control(null, [
        Validators.required,
        typeIsKnown
      ]),
      id_type: this.formBuilder.control('dynamic', Validators.required),
      id_key: this.formBuilder.control(null, Validators.required),
      id_prefix: this.formBuilder.control(''),
      concept_name_key: this.formBuilder.control(null),
      concept_name_prefix: this.formBuilder.control(''),
      concept_label_key: this.formBuilder.control(null),
      concept_label_prefix: this.formBuilder.control(''),
      mapping: this.formBuilder.array([]),
      include: this.formBuilder.control(true)
    });

    this.relationForm = this.formBuilder.group({
      id: this.formBuilder.control(''),
      alias: this.formBuilder.control('', Validators.required),
      description: this.formBuilder.control(''),
      relationship_type: this.formBuilder.control(null, Validators.required),
      id_type: this.formBuilder.control('dynamic', Validators.required),
      id_key: this.formBuilder.control(null, Validators.required),
      source: this.formBuilder.control(null, Validators.required),
      target: this.formBuilder.control(null, Validators.required),
      id_prefix: this.formBuilder.control(''),
      relationship_name_key: this.formBuilder.control(null),
      relationship_name_prefix: this.formBuilder.control(''),
      relationship_label_key: this.formBuilder.control(null),
      relationship_label_prefix: this.formBuilder.control(''),
      mapping: this.formBuilder.array([]),
      include: this.formBuilder.control(true)
    });

    this.viewForm = this.formBuilder.group({
      id: this.formBuilder.control(''),
      alias: this.formBuilder.control('', Validators.required),
      description: this.formBuilder.control(''),
      id_type: this.formBuilder.control('dynamic', Validators.required),
      id_key: this.formBuilder.control(null, Validators.required),
      view_name_type: this.formBuilder.control('static', Validators.required),
      id_prefix: this.formBuilder.control(''),
      view_name_key: this.formBuilder.control(null),
      view_name_prefix: this.formBuilder.control(''),
      view_name_value: this.formBuilder.control(''),
      view_label_key: this.formBuilder.control(null),
      view_label_prefix: this.formBuilder.control(''),
      view_layout: this.formBuilder.control(null, Validators.required),
      view_path: this.formBuilder.array([]),
      mapping: this.formBuilder.array([]),
      view_nodes: this.formBuilder.array([]),
      view_edges: this.formBuilder.array([]),
      include: this.formBuilder.control(true)
    });
  }

  private patchElementForm(definition: ElementDefinition) {
    this.resetElementForm();
    if (definition.mapping) {
      definition.mapping.forEach(() => {
        this.addMappingControl(this.elementForm);
      });
    }
    this.elementForm.patchValue(definition);
  }

  private resetElementForm() {
    (this.elementForm.controls.mapping as UntypedFormArray).controls.splice(0);
    this.elementForm.reset({ include: true, id_type: 'dynamic' });
  }

  private patchRelationForm(definition: RelationshipDefinition) {
    this.resetRelationForm();
    if (definition.mapping) {
      definition.mapping.forEach(() => {
        this.addMappingControl(this.relationForm);
      });
    }
    this.relationForm.patchValue(definition);
  }

  private resetRelationForm() {
    (this.relationForm.controls.mapping as UntypedFormArray).controls.splice(0);
    this.relationForm.reset({ include: true, id_type: 'dynamic' });
  }

  private patchViewForm(definition: ViewDefinition) {
    this.resetViewForm();
    if (definition.mapping) {
      definition.mapping.forEach(() => {
        this.addMappingControl(this.viewForm);
      });
    }
    if (definition.view_nodes) {
      definition.view_nodes.forEach(() => {
        this.addElementControl();
      });
    }
    if (definition.view_edges) {
      definition.view_edges.forEach(() => {
        this.addEdgeControl();
      });
    }
    if (definition.view_path) {
      definition.view_path.forEach(() => {
        this.addPathControl();
      });
    }
    this.viewForm.patchValue(definition);
  }

  private resetViewForm() {
    (this.viewForm.controls.mapping as UntypedFormArray).controls.splice(0);
    (this.viewForm.controls.view_nodes as UntypedFormArray).controls.splice(0);
    (this.viewForm.controls.view_edges as UntypedFormArray).controls.splice(0);
    (this.viewForm.controls.view_path as UntypedFormArray).controls.splice(0);
    this.viewForm.reset({ include: true, id_type: 'dynamic' });
  }

  private validateForm(form: UntypedFormGroup) {
    form.updateValueAndValidity();
    return form.valid;
  }

  set isQuickviewActive(state: boolean) {
    this.extractorService.update({
      description: 'Quickview active state changed',
      payload: {
        isQuickviewActive: state
      }
    });
  }

  set currentDefinitionType(type: DefinitionType) {
    this.isSubmitted = false;
    this.extractorService.update({
      description: 'Definition type updated',
      payload: {
        currentDefinitionType: type
      }
    });
  }
}
