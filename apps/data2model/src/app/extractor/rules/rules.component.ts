import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { faExclamationCircle, faExclamationTriangle, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { SortableTableShellConfig } from '@models4insight/components';
import { archimate3 } from '@models4insight/metamodel';
import { Feature } from '@models4insight/permissions';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { ExtractorRule, ValidationResult } from '../extractor-types';
import { ExtractorService } from '../extractor.service';
import { ValidationErrorSeverity } from '../rule-validators/validation-error';
import { RulesService } from './rules.service';
import { SaveRulesModalComponent } from './save-rules-modal/save-rules-modal.component';

const elementsTableConfig: SortableTableShellConfig = {
  error_column: { isStatic: true },
  alias: { description: 'The name of the rule', displayName: 'Rule name' },
  id_key: {
    description: 'The name of the column which has the concept ID',
    displayName: 'ID key'
  },
  id_prefix: {
    description: 'The prefix for the concept ID',
    displayName: 'ID prefix'
  },
  concept_type: {
    description: 'The ArchiMate type of the concept',
    displayName: 'Type'
  },
  include: {
    description: 'Whether or not the rule is included in the extracted model',
    displayName: 'Is active?'
  },
  description: {
    description: 'The description of the rule',
    displayName: 'Description'
  }
};

const relationsTableConfig: SortableTableShellConfig = {
  error_column: { isStatic: true },
  alias: { description: 'The name of the rule', displayName: 'Rule name' },
  id_key: {
    description: 'The name of the column which has the concept ID',
    displayName: 'ID key'
  },
  id_prefix: {
    description: 'The prefix for the concept ID',
    displayName: 'ID prefix'
  },
  source: {
    description: 'The name of the source rule',
    displayName: 'Source'
  },
  target: {
    description: 'The name of the target rule',
    displayName: 'Target'
  },
  relationship_type: {
    description: 'The ArchiMate type of the concept',
    displayName: 'Type'
  },
  include: {
    description: 'Whether or not the rule is included in the extracted model',
    displayName: 'Is active?'
  },
  description: {
    description: 'The description of the rule',
    displayName: 'Description'
  }
};

const viewsTableConfig: SortableTableShellConfig = {
  error_column: { isStatic: true },
  alias: { description: 'The name of the rule', displayName: 'Rule name' },
  id_key: {
    description: 'The name of the column which has the concept ID',
    displayName: 'ID key'
  },
  id_prefix: {
    description: 'The prefix for the concept ID',
    displayName: 'ID prefix'
  },
  include: {
    description: 'Whether or not the rule is included in the extracted model',
    displayName: 'Is active?'
  },
  description: {
    description: 'The description of the rule',
    displayName: 'Description'
  }
};

@Component({
  selector: 'models4insight-extractor-rules',
  templateUrl: 'rules.component.html',
  styleUrls: ['rules.component.scss']
})
export class RulesComponent implements OnInit, OnDestroy {
  @ViewChild(SaveRulesModalComponent, { static: true })
  private readonly saveRulesModal: SaveRulesModalComponent;

  readonly Feature = Feature;

  readonly elementTypes = archimate3.elements;
  readonly relationTypes = archimate3.relations;

  readonly faExclamationCircle = faExclamationCircle;
  readonly faExclamationTriangle = faExclamationTriangle;
  readonly faInfoCircle = faInfoCircle;

  currentHeaders$: Observable<string[]>;
  currentElementRules$: Observable<ExtractorRule[]>;
  currentRelationRules$: Observable<ExtractorRule[]>;
  currentValidationResult$: Observable<Dictionary<ValidationResult[]>>;
  currentViewRules$: Observable<ExtractorRule[]>;
  hasErrors$: Observable<boolean>;
  isExtractingModel$: Observable<boolean>;
  rules$: Observable<Dictionary<ExtractorRule>>;

  ValidationSeverityType = ValidationErrorSeverity;

  elementsTableConfig = elementsTableConfig;
  relationsTableConfig = relationsTableConfig;
  viewsTableConfig = viewsTableConfig;

  saveForm: UntypedFormGroup;

  constructor(
    private extractorService: ExtractorService,
    private rulesService: RulesService
  ) {
    this.initForm();
  }

  ngOnInit() {
    this.currentHeaders$ = this.extractorService.select('currentHeaders');
    this.currentElementRules$ = this.extractorService.elementRules;
    this.currentRelationRules$ = this.extractorService.relationRules;
    this.currentValidationResult$ = this.extractorService
      .select('validationResult')
      .pipe(shareReplay());
    this.currentViewRules$ = this.extractorService.viewRules;
    this.hasErrors$ = this.extractorService.hasErrors;
    this.isExtractingModel$ = this.extractorService.select('isExtractingModel');
    this.rules$ = this.extractorService.select(['rulesContext', 'rules']);
  }

  ngOnDestroy() {}

  extract() {
    this.extractorService.extract();
  }

  loadRules(files: FileList) {
    this.extractorService.loadRules(files.item(0));
  }

  openAddRuleQuickview() {
    this.extractorService.update({
      description: 'Add rule quickview opened',
      payload: {
        isQuickviewActive: true
      }
    });
  }

  selectRule(rule: ExtractorRule) {
    this.extractorService.selectRule(rule);
  }

  activateSaveRulesModal() {
    this.saveRulesModal.activate();
  }

  private initForm() {}
}
