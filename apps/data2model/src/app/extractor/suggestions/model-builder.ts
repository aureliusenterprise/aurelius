import { AbstractControl, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary, findKey, isEqual } from 'lodash';
import { BehaviorSubject, combineLatest, merge, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, first, map, startWith, switchMap } from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { FlaskService } from '../../api/flask.service';
import { DefinitionType, ElementDefinition, ExtractorDatasetEntry, ExtractorRule, ExtractorWorkerTask, RelationshipDefinition, SuggestedColumn, ValidationResult, ViewDefinition, ViewLayout } from '../extractor-types';
import { ExtractorService } from '../extractor.service';
import { BijacencyMapContext } from '../workers/bijacency-map';
import { SuggestionsService } from './suggestions.service';

export interface ModelBuilderContext {
  readonly id?: string;
  readonly bijacencyMap?: Dictionary<number>;
  readonly isGeneratingPreview?: boolean;
  readonly isUpdatingModelRules?: boolean;
  readonly isUpdatingViewRules?: boolean;
  readonly previewData?: Dictionary<Dictionary<any>>;
  readonly previewModel?: any;
  readonly reversed?: boolean;
  readonly selectedTab?: ModelBuilderTab;
}

export interface ModelFormContext {
  readonly relation?: {
    readonly name?: string;
    readonly type?: string;
  };
  readonly source?: {
    readonly type?: string;
  };
  readonly target?: {
    readonly type?: string;
  };
}

export type ModelBuilderTab = 'content' | 'views';

export type ViewContent = 'single' | 'source' | 'target';

export interface ViewFormContext {
  readonly content?: ViewContent;
  readonly key?: string;
  readonly layout?: ViewLayout;
}

interface DependentRules {
  readonly source?: string;
  readonly target?: string;
  readonly relation?: string;
  readonly view?: string;
}

function typeIsKnown({ value }: AbstractControl) {
  if (value === 'ar3_Unknown') {
    return { typeUnknown: true };
  }
  return null;
}

function propertyKeyDefined({ value }: UntypedFormGroup) {
  if (value.content === 'property' && !value.key) {
    return { propertyKeyUndefined: true };
  }
  return null;
}

const modelBuilderDefaultState: ModelBuilderContext = {
  reversed: false,
  selectedTab: 'content'
};

export class ModelBuilder extends BasicStore<ModelBuilderContext> {
  modelForm: UntypedFormGroup;
  viewForm: UntypedFormGroup;

  private dependentRules$: Subject<DependentRules> = new BehaviorSubject<
    DependentRules
  >({});
  private errors$: Subject<ValidationResult[]> = new BehaviorSubject<
    ValidationResult[]
  >([]);
  private generatePreview$: Subject<void> = new Subject<void>();

  constructor(
    private readonly id: string,
    private readonly extractorService: ExtractorService,
    private readonly flaskService: FlaskService,
    private readonly suggestionsService: SuggestionsService
  ) {
    super({ defaultState: modelBuilderDefaultState });
    Promise.all([
      this.createModelForm(this.id),
      this.createViewForm(this.id)
    ]).then(() => this.init());
  }

  private init() {
    merge(this.modelForm.valueChanges, this.select('reversed'))
      .pipe(
        startWith(this.modelForm.value),
        // Ensure that rapid updates dont cause excessive load
        debounceTime(100),
        switchMap(() => this.updateModelRules(this.id, this.modelForm.value)),
        untilDestroyed(this.suggestionsService)
      )
      .subscribe();

    merge(this.dependentRules$, this.viewForm.valueChanges)
      .pipe(
        startWith(this.viewForm.value),
        // Ensure that rapid updates dont cause excessive load
        debounceTime(100),
        switchMap(() => this.updateViewRules(this.id, this.viewForm.value)),
        untilDestroyed(this.suggestionsService)
      )
      .subscribe();

    this.generatePreview$
      .pipe(
        debounceTime(100),
        switchMap(() => this.handleGeneratePreviewModel(this.id)),
        untilDestroyed(this.suggestionsService)
      )
      .subscribe();

    // Whenever the rules change, evaluate whether any of the rules should be associated with this model builder
    this.extractorService
      .select(['rulesContext', 'rules'])
      .pipe(
        switchMap(rules => this.findDependentRules(rules)),
        distinctUntilChanged(isEqual)
      )
      .subscribe(this.dependentRules$);

    // Evaluate whether there are any validation errors whenever the dependencies or the validation result update
    combineLatest([
      this.dependentRules$,
      this.extractorService.select('validationResult')
    ])
      .pipe(
        map(([dependentRules, validationResult]) =>
          Object.values(dependentRules).reduce(
            (errors, ruleId) => [
              ...errors,
              ...(validationResult[ruleId] || [])
            ],
            [] as ValidationResult[]
          )
        )
      )
      .subscribe(this.errors$);

    // Update the form whenever the source rule changes
    this.dependentRules$
      .pipe(
        switchMap(({ source }) =>
          this.extractorService.select(['rulesContext', 'rules', source])
        ),
        distinctUntilChanged(isEqual)
      )
      .subscribe((sourceRule: ElementDefinition) =>
        this.modelForm.patchValue(
          {
            source: {
              type: sourceRule.concept_type
            }
          },
          { emitEvent: false }
        )
      );

    // Update the form whenever the target rule changes
    this.dependentRules$
      .pipe(
        switchMap(({ target }) =>
          this.extractorService.select(['rulesContext', 'rules', target])
        ),
        distinctUntilChanged(isEqual)
      )
      .subscribe((targetRule: ElementDefinition) =>
        this.modelForm.patchValue(
          {
            target: {
              type: targetRule.concept_type
            }
          },
          { emitEvent: false }
        )
      );

    // Update the form whenever the relationship rule changes
    this.dependentRules$
      .pipe(
        switchMap(({ relation }) =>
          this.extractorService.select(['rulesContext', 'rules', relation])
        ),
        distinctUntilChanged(isEqual)
      )
      .subscribe((relationRule: RelationshipDefinition) =>
        this.modelForm.patchValue(
          {
            relation: {
              name: (relationRule as any).relationship_name_key,
              type: relationRule.relationship_type
            }
          },
          { emitEvent: false }
        )
      );
  }

  /**
   * Deletes the rules which map to this suggestion.
   * The associated relationship and view rules are always deleted.
   * The source/target element rules are deleted if there are no other rules which use them.
   */
  async remove() {
    const [{ source, target, relation, view }, rules] = await Promise.all([
      this.dependentRules$.pipe(first()).toPromise(),
      this.extractorService.get(['rulesContext', 'rules'])
    ]);

    if (relation) {
      this.extractorService.delete({
        description: `Deleted relationship for suggestion ${this.id}`,
        path: ['rulesContext', 'rules', relation]
      });
    }

    if (view) {
      this.extractorService.delete({
        description: `Deleted view for suggestion ${this.id}`,
        path: ['rulesContext', 'rules', view]
      });
    }

    if (source && target) {
      const relationRules = Object.values(rules).filter(
        rule => rule.type === DefinitionType.RELATION
      ) as RelationshipDefinition[];
      const sourceRules = relationRules.filter((rule: RelationshipDefinition) =>
        [source, target].includes(rule.source)
      );
      const targetRules = relationRules.filter((rule: RelationshipDefinition) =>
        [source, target].includes(rule.target)
      );
      // Delete the element rules as well if there are no other relationships referring to them
      if (sourceRules.length === 1) {
        this.extractorService.delete({
          description: `Deleted the source element for suggestion ${this.id}`,
          path: ['rulesContext', 'rules', source]
        });

        this.extractorService.delete({
          description: `Deleted the column rule mapping for column ${source}`,
          path: ['columnRuleMapping', (source as any).id_key]
        });
      }
      if (targetRules.length === 1) {
        this.extractorService.delete({
          description: `Deleted the target element for suggestion ${this.id}`,
          path: ['rulesContext', 'rules', target]
        });

        this.extractorService.delete({
          description: `Deleted the column rule mapping for column ${target}`,
          path: ['columnRuleMapping', (target as any).id_key]
        });
      }
    }

    this.suggestionsService.delete({
      description: `Deleted model builder for suggestion ${this.id}`,
      path: ['modelBuilder', this.id]
    });
  }

  /**
   * Triggers the creation of a preview model.
   */
  generatePreviewModel() {
    this.generatePreview$.next();
  }

  /**
   * This is triggered whenever the reverse button is pressed
   */
  toggleReversed(relationshipId: string, currentState: boolean) {
    this.update({
      description: `Set reversed status for relationship ${relationshipId} to ${Boolean(
        !currentState
      )
        .toString()
        .toUpperCase()}`,
      payload: { reversed: !currentState }
    });
  }

  get errors() {
    return this.errors$.asObservable();
  }

  @ManagedTask('Updating the extractor rules', { isQuiet: true })
  @MonitorAsync('isUpdatingModelRules')
  private async updateModelRules(
    relationshipId: string,
    context: ModelFormContext
  ) {
    const [
      { source, target, relation },
      { source: sourceColumn, target: targetColumn },
      reversed,
      data,
      columns,
      valuesPerColumn
    ] = await Promise.all([
      this.dependentRules$.pipe(first()).toPromise(),
      this.extractorService.get(['suggestions', 'relations', relationshipId]),
      this.get('reversed'),
      this.extractorService.get('currentDataset'),
      this.extractorService.get(['suggestions', 'columns']),
      this.extractorService.get('valuesPerColumn')
    ]);

    const [sourceRule, targetRule, relationRule] = await Promise.all([
      this.extractorService.get(['rulesContext', 'rules', source], {
        includeFalsy: true
      }),
      this.extractorService.get(['rulesContext', 'rules', target], {
        includeFalsy: true
      }),
      this.extractorService.get(['rulesContext', 'rules', relation], {
        includeFalsy: true
      })
    ]);

    const updatedSourceColumnRule: ElementDefinition = {
      ...sourceRule,
      id: source ? source : uuid(),
      alias: `Element rule for column ${sourceColumn}`,
      description: `This rule generates a new element for every ${sourceColumn} in the dataset`,
      include: true,
      id_type: 'dynamic',
      id_prefix: 'element_',
      id_key: sourceColumn as string,
      type: DefinitionType.ELEMENT,
      concept_type: context.source.type,
      concept_name_key: sourceColumn as string
    };

    const updatedTargetColumnRule: ElementDefinition = {
      ...targetRule,
      id: target ? target : uuid(),
      alias: `Element rule for column ${targetColumn}`,
      description: `This rule generates a new element for every ${targetColumn} in the dataset`,
      include: true,
      id_type: 'dynamic',
      id_prefix: 'element_',
      id_key: targetColumn as string,
      type: DefinitionType.ELEMENT,
      concept_type: context.target.type,
      concept_name_key: targetColumn as string
    };

    /*
     * Use the bijacency between the source, target and name columns to determine the id_key for the relationship
     */
    const bijacencyMap = await this.calculateBijacencyMap(
      data,
      columns as SuggestedColumn[],
      sourceColumn as string,
      targetColumn as string,
      context.relation.name,
      valuesPerColumn
    );

    const bijacentIdKey = findKey(bijacencyMap, value => value === 1);

    const updatedRelationshipRule = {
      ...relationRule,
      id: relation ? relation : uuid(),
      type: DefinitionType.RELATION,
      alias: `Relationship rule between ${
        reversed ? targetColumn : sourceColumn
      } and ${reversed ? sourceColumn : targetColumn}`,
      description: `This rule generates a new relationship between  between ${
        reversed ? targetColumn : sourceColumn
      } and ${reversed ? sourceColumn : targetColumn}`,
      include: true,
      relationship_type: context.relation.type,
      id_type: bijacentIdKey ? 'dynamic' : 'static',
      id_prefix:
        relationRule &&
        relationRule.id_type === 'dynamic' &&
        relationRule.id_prefix
          ? relationRule.id_prefix
          : `relationship_${relationshipId}`,
      id_key:
        bijacentIdKey ||
        (context.relation.name
          ? [
              sourceColumn as string,
              context.relation.name,
              targetColumn as string
            ]
          : [sourceColumn as string, targetColumn as string]),
      id_value: context.relation.name
        ? [
            sourceColumn as string,
            context.relation.name,
            targetColumn as string
          ]
        : [sourceColumn as string, targetColumn as string],
      relationship_name_type: 'dynamic',
      relationship_name_key: context.relation.name,
      relationship_label_type: 'dynamic',
      relationship_label_key: context.relation.name,
      source: reversed
        ? updatedTargetColumnRule.id
        : updatedSourceColumnRule.id,
      target: reversed ? updatedSourceColumnRule.id : updatedTargetColumnRule.id
    };

    this.extractorService.saveRule(updatedSourceColumnRule);
    this.extractorService.saveRule(updatedTargetColumnRule);
    this.extractorService.saveRule(updatedRelationshipRule as any);

    this.generatePreviewModel();
  }

  @MonitorAsync('isUpdatingViewRules')
  private async updateViewRules(
    relationshipId: string,
    context: ViewFormContext
  ) {
    const [
      reversed,
      { source, target, view },
      { source: sourceColumn, target: targetColumn }
    ] = await Promise.all([
      this.get('reversed'),
      this.dependentRules$.pipe(first()).toPromise(),
      this.extractorService.get(['suggestions', 'relations', relationshipId])
    ]);

    if (source && target) {
      const [sourceRule, targetRule, viewRule] = await Promise.all([
        this.extractorService.get(['rulesContext', 'rules', source]),
        this.extractorService.get(['rulesContext', 'rules', target]),
        this.extractorService.get(['rulesContext', 'rules', view], {
          includeFalsy: true
        })
      ]);

      const updatedViewRule: ViewDefinition = {
        ...viewRule,
        id: view ? view : `view_${relationshipId}`,
        type: DefinitionType.VIEW,
        alias: `View rule between ${
          reversed ? targetColumn : sourceColumn
        } and ${reversed ? sourceColumn : targetColumn}`,
        description: `This rule generates a new view for every ${
          context.content === 'source'
            ? sourceColumn
            : context.content === 'target'
            ? targetColumn
            : context.key
        } in the dataset`,
        include: true,
        id_type: context.content === 'single' ? 'static' : 'dynamic',
        id_key:
          context.content === 'source'
            ? sourceColumn
            : context.content === 'target'
            ? targetColumn
            : context.key,
        id_value: `view_${relationshipId}`,
        id_prefix: `view_${relationshipId}`,
        view_name_type: context.content === 'single' ? 'static' : 'dynamic',
        view_name_key:
          context.content === 'source'
            ? sourceColumn
            : context.content === 'target'
            ? targetColumn
            : context.key,
        view_name_value: `View for the relationship between ${
          reversed ? targetColumn : sourceColumn
        } and ${reversed ? sourceColumn : targetColumn}`,
        view_layout: context.layout,
        view_nodes: [
          {
            rule: sourceRule.id
          },
          {
            rule: targetRule.id
          }
        ],
        view_edges: []
      } as any;

      this.extractorService.saveRule(updatedViewRule);

      this.generatePreviewModel();
    }
  }

  private async createModelForm(relationshipId: string) {
    // Look up any existing rules
    const [{ source, target, relation }] = await Promise.all([
      this.dependentRules$.pipe(first()).toPromise()
    ]);

    const [sourceRule, targetRule, relationRule] = await Promise.all([
      this.extractorService.get(['rulesContext', 'rules', source], {
        includeFalsy: true
      }),
      this.extractorService.get(['rulesContext', 'rules', target], {
        includeFalsy: true
      }),
      this.extractorService.get(['rulesContext', 'rules', relation], {
        includeFalsy: true
      })
    ]);

    const modelForm = new UntypedFormGroup({
      relation: new UntypedFormGroup({
        name: new UntypedFormControl(''),
        type: new UntypedFormControl(
          relationRule
            ? (relationRule as RelationshipDefinition).relationship_type
            : 'o',
          [Validators.required, typeIsKnown]
        )
      }),
      source: new UntypedFormGroup({
        type: new UntypedFormControl(
          sourceRule
            ? (sourceRule as ElementDefinition).concept_type
            : 'ar3_Unknown',
          [Validators.required, typeIsKnown]
        )
      }),
      target: new UntypedFormGroup({
        type: new UntypedFormControl(
          targetRule
            ? (targetRule as ElementDefinition).concept_type
            : 'ar3_Unknown',
          [Validators.required, typeIsKnown]
        )
      })
    });

    this.modelForm = modelForm;
  }

  private async createViewForm(relationshipId: string) {
    const [{ source, target }, { view }] = await Promise.all([
      this.extractorService.get(['suggestions', 'relations', relationshipId]),
      this.dependentRules$.pipe(first()).toPromise()
    ]);

    const existingViewRule = await this.extractorService.get(
      ['rulesContext', 'rules', view],
      { includeFalsy: true }
    );

    const viewForm = new UntypedFormGroup(
      {
        content: new UntypedFormControl(
          existingViewRule
            ? existingViewRule.id_type === 'static'
              ? 'single'
              : existingViewRule.id_key === source
              ? 'source'
              : existingViewRule.id_key === target
              ? 'target'
              : 'property'
            : 'source',
          [Validators.required]
        ),
        key: new UntypedFormControl(
          existingViewRule &&
          existingViewRule.id_type === 'dynamic' &&
          existingViewRule.id_key !== source &&
          existingViewRule.id_key !== target
            ? existingViewRule.id_key
            : null
        ),
        layout: new UntypedFormControl(ViewLayout.ARCHIMATE_HIERARCHICAL, [
          Validators.required
        ])
      },
      [propertyKeyDefined]
    );
    this.viewForm = viewForm;
  }

  private async calculateBijacencyMap(
    data: ExtractorDatasetEntry[],
    columns: SuggestedColumn[],
    source: string,
    target: string,
    name: string,
    valuesPerColumn: Dictionary<any[]>
  ) {
    const worker = new Worker(new URL('../workers/extractor.worker.ts', import.meta.url), {
      type: 'module'
    });

    const result = new Promise<Dictionary<number>>((resolve, reject) => {
      worker.onmessage = ({ data }) => resolve(data);

      worker.onerror = ({ error }) => reject(error);
    });

    worker.postMessage({
      task: ExtractorWorkerTask.BIJACENCY_MAP,
      context: {
        data,
        columns,
        source,
        target,
        name,
        valuesPerColumn
      } as BijacencyMapContext
    });

    return result;
  }

  @MonitorAsync('isGeneratingPreview')
  @ManagedTask('Generating a preview model', { isQuiet: true })
  private async handleGeneratePreviewModel(relationshipId: string) {
    const [data, rules, source, target] = await Promise.all([
      this.extractorService.get('currentDataset'),
      this.extractorService.get(['rulesContext', 'rules']),
      this.extractorService.get([
        'suggestions',
        'relations',
        relationshipId,
        'source'
      ]),
      this.extractorService.get([
        'suggestions',
        'relations',
        relationshipId,
        'target'
      ])
    ]);

    /**
     * Lookup the element rules for the source and target elements.
     */
    const lookupColumnRule = async (columnName: string) => {
      const ruleId = await this.extractorService.get([
        'columnRuleMapping',
        columnName
      ]);
      return rules[ruleId];
    };

    const [sourceColumnRule, targetColumnRule] = await Promise.all([
      lookupColumnRule(source as string),
      lookupColumnRule(target as string)
    ]);

    // Continue only of the source and target rules exist
    if (sourceColumnRule && targetColumnRule) {
      const relationshipRule = Object.values(rules)
        .filter(rule => rule.type === DefinitionType.RELATION)
        .find(
          (rule: RelationshipDefinition) =>
            [sourceColumnRule.id, targetColumnRule.id].includes(rule.source) &&
            [sourceColumnRule.id, targetColumnRule.id].includes(rule.target)
        );
      /**
       * Lookup whether there is any view definition which contains these two rules
       */
      const viewRule = Object.values(rules).find(
        rule =>
          rule.type === DefinitionType.VIEW &&
          rule.view_nodes
            .map(node => node.rule)
            .includes(sourceColumnRule.id) &&
          rule.view_nodes.map(node => node.rule).includes(targetColumnRule.id)
      ) as ViewDefinition;

      // Continue only if the relationship and view rules exist
      if (relationshipRule && viewRule) {
        /**
         * Generate a preview model based on the current rules and a small slice of the data
         */
        const { model, metadata } = await this.flaskService
          .extract(data.slice(0, 5), {
            elements: [
              sourceColumnRule,
              targetColumnRule
            ] as ElementDefinition[],
            relations: [relationshipRule] as RelationshipDefinition[],
            views: [viewRule] as ViewDefinition[]
          })
          .toPromise();

        const previewModel = JSON.parse(model);

        const previewData = {};
        for (const { id: conceptId, data: conceptData } of metadata) {
          previewData[conceptId] = conceptData;
        }

        this.update({
          description: 'New preview model available',
          payload: { previewModel, previewData }
        });
      }
    }
  }

  private async findDependentRules(rules: Dictionary<ExtractorRule>) {
    const [{ source, target }] = await Promise.all([
      this.extractorService.get(['suggestions', 'relations', this.id])
    ]);

    const lookupColumnRuleId = async (columnName: string) =>
      this.extractorService.get(['columnRuleMapping', columnName], {
        includeFalsy: true
      });

    const [sourceColumnRuleId, targetColumnRuleId] = await Promise.all([
      lookupColumnRuleId(source as string),
      lookupColumnRuleId(target as string)
    ]);

    const [sourceColumnRule, targetColumnRule] = await Promise.all([
      this.extractorService.get(['rulesContext', 'rules', sourceColumnRuleId], {
        includeFalsy: true
      }),
      this.extractorService.get(['rulesContext', 'rules', targetColumnRuleId], {
        includeFalsy: true
      })
    ]);

    const mappedRelation = Object.values(rules)
      .filter(rule => rule.type === DefinitionType.RELATION)
      .find(
        (rule: RelationshipDefinition) =>
          [sourceColumnRuleId, targetColumnRuleId].includes(rule.source) &&
          [sourceColumnRuleId, targetColumnRuleId].includes(rule.target) &&
          (rule as any).id_prefix.includes('relationship_')
      );

    const mappedView = Object.values(rules)
      .filter(rule => rule.type === DefinitionType.VIEW)
      .find(
        (view: ViewDefinition) =>
          view.view_nodes.map(node => node.rule).includes(sourceColumnRuleId) &&
          view.view_nodes.map(node => node.rule).includes(targetColumnRuleId) &&
          (view as any).id_prefix.includes('view_')
      );

    return {
      source: sourceColumnRule ? sourceColumnRule.id : null,
      target: targetColumnRule ? targetColumnRule.id : null,
      relation: mappedRelation ? mappedRelation.id : null,
      view: mappedView ? mappedView.id : null
    } as DependentRules;
  }
}
