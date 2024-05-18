import { Injectable } from '@angular/core';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { Router } from '@angular/router';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { CommitModelService, ModelDataCommitService, ModelDataService, ModelService } from '@models4insight/services/model';
import { ManagedTask } from '@models4insight/task-manager';
import { groupBy, readFileAsString, userAgentIsInternetExplorer } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest, Observable, Subject } from 'rxjs';
import { debounceTime, exhaustMap, filter, map, switchMap, withLatestFrom } from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { FlaskService } from '../api/flask.service';
import { DefinitionType, ElementDefinition, ExtractorDatasetEntry, ExtractorRule, ExtractorWorkerTask, ModelCommitContext, RelationshipDefinition, RulesContext, SuggestedRelation, Suggestions, ValidationResult, ValidationSeverityType, ViewDefinition } from './extractor-types';
import { SuggestionsContext } from './workers/suggestions';

export interface ExtractorStoreContext {
  readonly currentDataset?: ExtractorDatasetEntry[];
  readonly currentDefinitionType?: DefinitionType;
  readonly currentHeaders?: string[];
  readonly currentRulesFileName?: string;
  readonly currentRulesObjectURL?: SafeUrl;
  readonly columnRuleMapping?: Dictionary<string>;
  readonly isCalculatingSuggestions?: boolean;
  readonly isCommitingModel?: boolean;
  readonly isExtractingModel?: boolean;
  readonly isQuickviewActive?: boolean;
  readonly isUpdatingRules?: boolean;
  readonly rulesContext?: RulesContext;
  readonly selectedSuggestion?: SuggestedRelation;
  readonly suggestions?: Suggestions;
  readonly validationResult?: Dictionary<ValidationResult[]>;
  readonly valuesPerColumn?: Dictionary<any[]>;
}

const defaultState = {
  currentDefinitionType: DefinitionType.ELEMENT,
  columnRuleMapping: {},
  isCalculatingSuggestions: false,
  isCommitingModel: false,
  isQuickviewActive: false,
  isUpdatingRules: false,
  isExtractingModel: false,
  rulesContext: {
    rules: {}
  }
};

@Injectable()
export class ExtractorService extends BasicStore<ExtractorStoreContext> {
  private readonly commit$: Subject<ModelCommitContext> = new Subject<
    ModelCommitContext
  >();
  private readonly extract$: Subject<void> = new Subject<void>();
  private readonly loadRules$: Subject<File> = new Subject<File>();
  private readonly ruleSelected$: Subject<ExtractorRule> = new Subject<
    ExtractorRule
  >();

  constructor(
    private readonly modelService: ModelService,
    private readonly modelCommitService: CommitModelService,
    private readonly modelDataService: ModelDataService,
    private readonly modelDataCommitService: ModelDataCommitService,
    private readonly flaskService: FlaskService,
    private readonly router: Router,
    private readonly sanitizer: DomSanitizer,
    storeService: StoreService
  ) {
    super({ defaultState, name: 'ExtractorService', storeService });
    this.init();
  }

  private init() {
    // Whenever the dataset updates, calculate the set of headers
    this.select('currentDataset')
      .pipe(
        // Compile a set of headers from all rows in the current dataset.
        // Assume that no single row necessarily contains all headers.
        map(dataset =>
          Array.from(
            dataset.reduce(
              (headers: Set<string>, row: ExtractorDatasetEntry) => {
                // Add each header of the current row to the set of headers
                Object.keys(row).forEach(header => headers.add(header));
                // Return the set
                return headers;
              },
              new Set<string>()
            ) as Set<string>
          )
        )
      )
      .subscribe(headers => {
        this.update({
          description: 'New headers available',
          payload: {
            currentHeaders: headers
          }
        });
      });

    // Whenever the dataset or the headers update, calculate the values per column for use with the bijacency metrics
    combineLatest([
      this.select('currentDataset'),
      this.select('currentHeaders')
    ]).subscribe(([dataset, headers]) =>
      this.indexValuesPerColumn(dataset, headers)
    );

    // Whenever an extract is triggered, request an extracted model from the API based on the current dataset and rules
    this.extract$
      .pipe(
        withLatestFrom(
          this.select('currentDataset'),
          // Only take the rules that are currently active
          this.select(['rulesContext', 'rules']).pipe(
            map((rules: Dictionary<ExtractorRule>) =>
              Object.values(rules).filter((rule: ExtractorRule) => rule.include)
            )
          ),
          // Check whether there are any errors in the current validation result
          this.hasErrors
        ),
        // Continue only if there are no errors in the validation result
        filter(([, , , hasErrors]) => !hasErrors),
        switchMap(([, data, rules]) => this.handleExtract(data, rules))
      )
      .subscribe();

    // Whenever a commit is triggered, upload the current model to the repository
    this.commit$
      .pipe(exhaustMap(context => this.handleCommit(context)))
      .subscribe();

    // Whenever load rules is triggered, load the rules
    this.loadRules$
      .pipe(exhaustMap(rules => this.handleLoadRules(rules)))
      .subscribe();

    // Whenever a rule is selected, open the quickview and set the appropriate tab
    this.onRuleSelected.subscribe(rule =>
      this.update({
        description: 'New rule selected',
        payload: {
          currentDefinitionType: rule.type,
          isQuickviewActive: true
        }
      })
    );

    // Whenever the current rules change, validate them
    this.select(['rulesContext', 'rules'])
      .pipe(
        withLatestFrom(this.elementRules, this.relationRules, this.viewRules),
        switchMap(([, elementRules, relationRules, viewRules]) =>
          this.validateRules(elementRules, relationRules, viewRules)
        )
      )
      .subscribe();

    // Whenever the element rules change, map the colums in the dataset to the current element rules
    this.elementRules
      .pipe(switchMap(elements => this.updateColumnRuleMapping(elements)))
      .subscribe();

    // Whenever the rules context changes, generate an object URL so it can be saved by the user
    this.select('rulesContext')
      .pipe(debounceTime(20))
      .subscribe(rules =>
        this.update({
          description: 'New rules object URL available',
          payload: {
            currentRulesFileName: `d2m - ${
              rules.name
            } - ${new Date().toLocaleString()}.json`,
            currentRulesObjectURL: this.sanitizer.bypassSecurityTrustUrl(
              `data:text/json;charset=UTF-8,${encodeURIComponent(
                JSON.stringify(rules)
              )}`
            )
          }
        })
      );

    // Whenever the dataset updates, generate a new set of suggestions
    this.select('currentDataset')
      .pipe(switchMap(data => this.calculateSuggestions(data)))
      .subscribe(suggestions =>
        this.update({
          description: 'New suggestions available',
          payload: {
            suggestions: suggestions
          }
        })
      );
  }

  selectRule(rule: ExtractorRule) {
    this.ruleSelected$.next(rule);
  }

  /**
   * Triggers a commit of the current model
   */
  commitModel(context: ModelCommitContext) {
    this.commit$.next(context);
  }

  /**
   * Trigger the model extraction based on the current data and rules
   */
  extract() {
    this.extract$.next();
  }

  /**
   * Add a new extractor rule to the list of rules
   * @param rule the rule to add
   */
  saveRule(rule: ExtractorRule) {
    if (!rule.id) {
      rule = Object.assign(rule, { id: uuid() });
    }
    this.update({
      description: 'Rule saved',
      path: ['rulesContext', 'rules', rule.id],
      payload: rule
    });
  }

  /**
   * Remove an existing extractor rule from the list of rules
   * @param rule the rule to remove
   */
  deleteRule(rule: ExtractorRule) {
    this.delete({
      description: 'Rule deleted',
      path: ['rulesContext', 'rules', rule.id]
    });
  }

  /**
   * Loads and applies a ruleset from a File
   * @param rules
   */
  loadRules(rules: File) {
    this.loadRules$.next(rules);
  }

  /** Updates the current dataset. Resets the current state. */
  updateDataset(dataset: ExtractorDatasetEntry[]) {
    this.reset();
    this.update({
      description: 'New dataset available',
      payload: {
        currentDataset: dataset
      }
    });
  }

  @MonitorAsync('isCommitingModel')
  private async handleCommit(context: ModelCommitContext): Promise<any> {
    await this.modelDataCommitService.commitData(context.branchName);

    const model = await this.modelService.get('model');

    return this.modelCommitService.commitJsonModel(
      context.branchName,
      context.comment,
      model,
      { conflictResolutionTemplate: context.conflictResolutionTemplate }
    );
  }

  @MonitorAsync('isExtractingModel')
  @ManagedTask('Extracting a model from the data')
  private async handleExtract(data: Dictionary<any>[], rules: ExtractorRule[]) {
    const { metadata, model } = await this.flaskService
      .extract(data, {
        elements: rules.filter(
          rule => rule.type === DefinitionType.ELEMENT
        ) as ElementDefinition[],
        relations: rules.filter(
          rule => rule.type === DefinitionType.RELATION
        ) as RelationshipDefinition[],
        views: rules.filter(
          rule => rule.type === DefinitionType.VIEW
        ) as ViewDefinition[]
      })
      .toPromise();

    this.modelService.model = JSON.parse(model);

    const dataByConceptId = {};
    for (const { id: conceptId, data: conceptData } of metadata) {
      dataByConceptId[conceptId] = conceptData;
    }

    this.modelDataService.dataByConceptId = dataByConceptId;

    this.router.navigate(['home', 'model']);
  }

  @MonitorAsync('isUpdatingRules')
  @ManagedTask('Loading the rules')
  private async handleLoadRules(sourceFile: File) {
    const rules = await readFileAsString(sourceFile);
    this.update({
      description: 'New rules imported',
      payload: {
        rulesContext: JSON.parse(rules)
      }
    });
  }

  @MonitorAsync('isCalculatingSuggestions')
  @ManagedTask('Calculating suggested relationships based on your data', {
    // Suggestions are not supported in IE. Hide any associated errors.
    clearOnError: userAgentIsInternetExplorer(),
    isQuiet: true
  })
  private async calculateSuggestions(data: Dictionary<any>[]) {
    const worker = new Worker(new URL('./workers/extractor.worker.ts', import.meta.url), {
      type: 'module'
    });

    const result = new Promise<Suggestions>((resolve, reject) => {
      worker.onmessage = ({ data }) => resolve(data);

      worker.onerror = ({ error }) => reject(error);
    });

    worker.postMessage({
      task: ExtractorWorkerTask.SUGGESTIONS,
      context: { data: data } as SuggestionsContext
    });

    return result;
  }

  @MonitorAsync('isValidatingRules')
  private async validateRules(
    elementRules: ElementDefinition[],
    relationRules: RelationshipDefinition[],
    viewRules: ViewDefinition[]
  ) {
    // Check whether any rules of the same category use the same ID column and prefix
    const [
      duplicateElements,
      duplicateRelations,
      duplicateViews
    ] = await Promise.all([
      this.findDuplicates(elementRules),
      this.findDuplicates(relationRules),
      this.findDuplicates(viewRules)
    ]);

    const duplicates: ValidationResult[] = [
      ...duplicateElements,
      ...duplicateRelations,
      ...duplicateViews
    ].map(duplicate => ({
      type: ValidationSeverityType.WARNING,
      rule: duplicate.id,
      description: `This ${duplicate.type} will be ignored during extraction because its identifier overlaps with that of another ${duplicate.type}.`
    }));

    // Check whether any elements do not have an assigned type
    const untypedElements = elementRules
      .filter(element => element.concept_type === 'ar3_Unknown')
      .map(element => ({
        type: ValidationSeverityType.ERROR,
        rule: element.id,
        description: `This ${element.type} is invalid because it does not have an assigned type.`
      }));

    // Check whether any rules of another category use the same ID column and prefix
    const [
      intersectingElements,
      intersectingRelations,
      intersectingViews
    ] = await Promise.all([
      this.findIntersections(elementRules, ...relationRules, ...viewRules),
      this.findIntersections(relationRules, ...elementRules, ...viewRules),
      this.findIntersections(viewRules, ...elementRules, ...relationRules)
    ]);

    const intersections: ValidationResult[] = [
      ...intersectingElements,
      ...intersectingRelations,
      ...intersectingViews
    ].map(intersection => ({
      type: ValidationSeverityType.ERROR,
      rule: intersection.id,
      description: `This ${intersection.type} is invalid because its identifier overlaps with that of another rule that is not a ${intersection.type}.`
    }));

    //Check whether any relations originate from elements that are not defined in the extractor rules
    const unmappedSources = relationRules
      .filter(
        relationRule =>
          elementRules.length === 0 ||
          undefined ===
            elementRules.find(
              elementRule => elementRule.id === relationRule.source
            )
      )
      .map(relation => ({
        type: ValidationSeverityType.ERROR,
        rule: relation.id,
        description: `The source of this relation is not defined in the extractor rules`
      }));

    //Check whether any relations end with elements that are not defined in the extractor rules
    const unmappedTargets = relationRules
      .filter(
        relationRule =>
          elementRules.length === 0 ||
          undefined ===
            elementRules.find(
              elementRule => elementRule.id === relationRule.target
            )
      )
      .map(relation => ({
        type: ValidationSeverityType.ERROR,
        rule: relation.id,
        description: `This target of this relation is not defined in the extractor rules`
      }));

    // Check whether any views include references to elements that are not defined in the extractor rules
    const unmappedViewNodes = viewRules
      .filter(
        viewRule =>
          (viewRule.view_nodes.length > 0 && elementRules.length === 0) ||
          !!viewRule.view_nodes.find(
            node =>
              undefined ===
              elementRules.find(elementRule => elementRule.id === node.rule)
          )
      )
      .map(node => ({
        type: ValidationSeverityType.ERROR,
        rule: node.id,
        description: `This view contains nodes that are not defined in the extractor rules`
      }));

    // Check whether any views include references to relations that are not defined in the extractor rules
    const unmappedViewEdges = viewRules
      .filter(
        viewRule =>
          (viewRule.view_edges.length > 0 && relationRules.length === 0) ||
          viewRule.view_edges.find(
            edge =>
              undefined ===
              relationRules.find(relationRule => relationRule.id === edge.rule)
          )
      )
      .map(edge => ({
        type: ValidationSeverityType.ERROR,
        rule: edge.id,
        description: `This view contains edges that are not defined in the extractor rules`
      }));

    const validationResult = groupBy(
      [
        ...intersections,
        ...duplicates,
        ...untypedElements,
        ...unmappedSources,
        ...unmappedTargets,
        ...unmappedViewNodes,
        ...unmappedViewEdges
      ],
      'rule'
    );

    this.update({
      description: 'New validation result available',
      payload: { validationResult }
    });
  }

  private async findDuplicates(rules: ExtractorRule[]) {
    return rules.filter((rule, index, rules) =>
      rules
        .slice(index + 1)
        .find(
          other =>
            rule.id_type === 'dynamic' &&
            other.id_type === 'dynamic' &&
            rule.id_key === other.id_key &&
            ((!rule.id_prefix && !other.id_prefix) ||
              rule.id_prefix === other.id_prefix)
        )
    );
  }

  private async findIntersections(
    rules: ExtractorRule[],
    ...others: ExtractorRule[]
  ) {
    return rules.filter(rule =>
      others.find(
        other =>
          rule.id_type === 'dynamic' &&
          other.id_type === 'dynamic' &&
          rule.id_key === other.id_key &&
          ((!rule.id_prefix && !other.id_prefix) ||
            rule.id_prefix === other.id_prefix)
      )
    );
  }

  private async updateColumnRuleMapping(elements: ElementDefinition[]) {
    const columnRuleMapping = elements
      .filter(
        (element: any) =>
          element.id_key &&
          element.id_prefix &&
          element.id_prefix.includes('element_')
      )
      .reduce(
        (mapping, element: any) => ({
          ...mapping,
          [element.id_key]: element.id
        }),
        {}
      );

    this.update({
      description: `Column rule mapping updated`,
      payload: { columnRuleMapping }
    });
  }

  private indexValuesPerColumn(
    dataset: ExtractorDatasetEntry[],
    headers: string[]
  ) {
    const valuesPerColumn = {};

    for (const header of headers) {
      const values = dataset.map(row => row[header]);
      valuesPerColumn[header] = values;
    }

    this.update({
      description: 'Calculated unique values per column in the dataset',
      payload: {
        valuesPerColumn
      }
    });
  }

  get elementRules(): Observable<ElementDefinition[]> {
    return this.select(['rulesContext', 'rules'], { includeFalsy: true }).pipe(
      map(
        (rules: Dictionary<ExtractorRule>) =>
          Object.values(rules).filter(
            (rule: ExtractorRule) => rule.type === DefinitionType.ELEMENT
          ) as ElementDefinition[]
      )
    );
  }

  get hasErrors(): Observable<boolean> {
    return this.select('validationResult').pipe(
      map(
        validationResult =>
          // Check whether there are any rules with validation results of level ERROR
          Object.values(validationResult).filter(items =>
            items.some(item => item.type === ValidationSeverityType.ERROR)
          ).length > 0
      )
    );
  }

  get relationRules(): Observable<RelationshipDefinition[]> {
    return this.select(['rulesContext', 'rules'], { includeFalsy: true }).pipe(
      map(
        (rules: Dictionary<ExtractorRule>) =>
          Object.values(rules).filter(
            (rule: ExtractorRule) => rule.type === DefinitionType.RELATION
          ) as RelationshipDefinition[]
      )
    );
  }

  get viewRules(): Observable<ViewDefinition[]> {
    return this.select(['rulesContext', 'rules'], { includeFalsy: true }).pipe(
      map(
        (rules: Dictionary<ExtractorRule>) =>
          Object.values(rules).filter(
            (rule: ExtractorRule) => rule.type === DefinitionType.VIEW
          ) as ViewDefinition[]
      )
    );
  }

  get onRuleSelected() {
    return this.ruleSelected$.asObservable();
  }
}
