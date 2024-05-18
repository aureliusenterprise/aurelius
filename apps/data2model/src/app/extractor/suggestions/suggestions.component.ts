import { Component, OnDestroy, OnInit } from '@angular/core';
import { faExchangeAlt, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { SortableTableShellConfig } from '@models4insight/components';
import { Logger } from '@models4insight/logger';
import { archimate3, toHumanReadableNames } from '@models4insight/metamodel';
import { untilDestroyed, userAgentIsInternetExplorer } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { filter, map, shareReplay, switchMap } from 'rxjs/operators';
import { ElementDefinition, ExtractorRule, RelationshipDefinition, SuggestedColumn, SuggestedRelation, ViewDefinition, ViewLayout } from '../extractor-types';
import { ExtractorService } from '../extractor.service';
import { ModelBuilder, ModelBuilderContext, ModelBuilderTab } from './model-builder';
import { RelationshipTypeTab, SuggestionsService } from './suggestions.service';
import { CanonicalView } from '@models4insight/services/model';

const log = new Logger('SuggestionsComponent');

const suggestionsTableConfig: SortableTableShellConfig = {
  index: {
    displayName: '#',
    description:
      'Suggestions are numbered by relevance, with #1 being the most relevant'
  },
  source: {
    displayName: 'Source',
    description:
      'The name of the column which defines the origin of the relationship'
  },
  target: {
    displayName: 'Target',
    description:
      'The name of the column which defines the destination of the relationship'
  },
  errors: {
    isNarrow: true,
    isStatic: true
  }
};

@Component({
  selector: 'models4insight-suggestions',
  templateUrl: 'suggestions.component.html',
  styleUrls: ['suggestions.component.scss']
})
export class SuggestionsComponent implements OnInit, OnDestroy {
  readonly elementTypes = Object.entries(
    toHumanReadableNames(archimate3.elements)
  );
  readonly relationshipTypes = Object.entries(
    toHumanReadableNames(archimate3.relations)
  );

  readonly forwardDisplayNames = {
    a: 'accesses',
    ar: 'reads from',
    aw: 'writes to',
    arw: 'reads from and writes to',
    g: 'aggregates',
    i: 'assigned to',
    o: 'associated with',
    do: 'associated with (directed)',
    c: 'composes',
    f: 'flows into',
    n: 'influences',
    r: 'realizes',
    v: 'serves',
    s: 'specializes',
    t: 'triggers'
  };

  readonly reverseDisplayNames = {
    a: 'accessed by',
    ar: 'read by',
    aw: 'written to by',
    arw: 'read by and written to by',
    g: 'aggregated by',
    i: 'is assigned',
    o: 'associated with',
    do: 'associated with (directed)',
    c: 'composed by',
    f: 'flows from',
    n: 'influenced by',
    r: 'realized by',
    v: 'served by',
    s: 'specialized by',
    t: 'triggered by'
  };

  readonly viewLayouts = Object.entries({
    [ViewLayout.ARCHIMATE_HIERARCHICAL]: 'Hierarchical',
    [ViewLayout.ARCHIMATE_PROCESS]: 'Process'
  });

  readonly suggestionsTableConfig = suggestionsTableConfig;

  readonly userAgentIsInternetExplorer = userAgentIsInternetExplorer();

  readonly faExchangeAlt = faExchangeAlt;
  readonly faSpinner = faSpinner;

  suggestedRelations$: Observable<Dictionary<SuggestedRelation>>;
  dynamicRelations$: Observable<SuggestedRelation[]>;
  dynamicRelationRanks$: Observable<Dictionary<number>>;
  isCalculatingBijacencies$: Observable<boolean>;
  isCalculatingSuggestions$: Observable<boolean>;
  isExtractingModel$: Observable<boolean>;
  isUpdatingModelRules$: Observable<boolean>;
  isUpdatingViewRules$: Observable<boolean>;
  labels$: Observable<SuggestedColumn[]>;
  otherRelations$: Observable<SuggestedRelation[]>;
  otherRelationRanks$: Observable<Dictionary<number>>;
  selectedRelationship$: Observable<SuggestedRelation>;
  selectedTab$: Observable<RelationshipTypeTab>;
  structuralRelations$: Observable<SuggestedRelation[]>;
  structuralRelationRanks$: Observable<Dictionary<number>>;
  currentRules$: Observable<ExtractorRule[]>;
  sourceRule$: Observable<ElementDefinition>;
  targetRule$: Observable<ElementDefinition>;
  relationshipRule$: Observable<RelationshipDefinition>;
  viewRule$: Observable<ViewDefinition>;
  modelBuilder$: Observable<ModelBuilder>;
  modelBuilderContext$: Observable<ModelBuilderContext>;
  modelBuilderIndex$: Observable<Dictionary<ModelBuilder>>;
  hasErrors$: Observable<boolean>;


  isSubmitted = false;

  constructor(
    private extractorService: ExtractorService,
    private suggestionsService: SuggestionsService
  ) {}

  ngOnInit() {
    const relationships$ = this.extractorService
      .select(['suggestions', 'relations'])
      .pipe(
        map(relationships => Object.values(relationships)),
        shareReplay(1)
      );

    this.dynamicRelations$ = relationships$.pipe(
      map(
        relations => relations.filter(relation => relation.type === 'dynamic'),
        shareReplay()
      )
    );

    this.dynamicRelationRanks$ = this.dynamicRelations$.pipe(
      map(relations =>
        relations.reduce(
          (result, relation, index) => ({
            ...result,
            [relation.id]: index + 1
          }),
          {}
        )
      ),
      shareReplay()
    );

    this.otherRelations$ = relationships$.pipe(
      map(relations => relations.filter(relation => relation.type === 'other')),
      shareReplay()
    );

    this.otherRelationRanks$ = this.otherRelations$.pipe(
      map(relations =>
        relations.reduce(
          (result, relation, index) => ({
            ...result,
            [relation.id]: index + 1
          }),
          {}
        )
      ),
      shareReplay()
    );

    this.structuralRelations$ = relationships$.pipe(
      map(relations =>
        relations.filter(relation => relation.type === 'structural')
      ),
      shareReplay()
    );

    this.structuralRelationRanks$ = this.structuralRelations$.pipe(
      map(relations =>
        relations.reduce(
          (result, relation, index) => ({
            ...result,
            [relation.id]: index + 1
          }),
          {}
        )
      ),
      shareReplay()
    );

    this.selectedRelationship$ = combineLatest([
      this.suggestionsService.select('selectedRelationship', {
        includeFalsy: true
      }),
      this.extractorService.select(['suggestions', 'relations'])
    ]).pipe(
      map(([id, relations]) => (id ? relations[id] : null)),
      shareReplay()
    );

    this.modelBuilder$ = this.selectedRelationship$.pipe(
      filter(relation => !!relation),
      switchMap(relation =>
        this.suggestionsService.select(['modelBuilder', relation.id], {
          includeFalsy: true
        })
      ),
      shareReplay()
    );

    this.modelBuilderContext$ = this.modelBuilder$.pipe(
      filter(builder => !!builder),
      switchMap(builder => builder.state),
      shareReplay()
    );

    this.isCalculatingSuggestions$ = this.extractorService.select(
      'isCalculatingSuggestions'
    );

    this.isUpdatingModelRules$ = this.suggestionsService
      .select('isUpdatingModelRules', { includeFalsy: true })
      .pipe(shareReplay());

    // For whatever reason, subscribing to the state here ensures the UI gets updated every single time the reverse button is clicked.
    this.isUpdatingModelRules$.pipe(untilDestroyed(this)).subscribe(state =>
      log.debug(
        `Is updating model rules: ${Boolean(state)
          .toString()
          .toUpperCase()}`
      )
    );

    this.isUpdatingViewRules$ = this.suggestionsService
      .select('isUpdatingViewRules', { includeFalsy: true })
      .pipe(shareReplay());

    this.suggestedRelations$ = this.extractorService.select([
      'suggestions',
      'relations'
    ]);

    this.isExtractingModel$ = this.extractorService.select('isExtractingModel');
    this.labels$ = this.extractorService.select(['suggestions', 'labels']);
    this.selectedTab$ = this.suggestionsService.select('selectedTab');
    this.modelBuilderIndex$ = this.suggestionsService.select('modelBuilder').pipe(shareReplay());

    this.hasErrors$ = this.extractorService.hasErrors;
  }

  ngOnDestroy() {}

  /**
   * This is triggered whenever the extract button is pressed
   */
  extract() {
    this.extractorService.extract();
  }

  removeRelation(event: boolean, modelBuilder: ModelBuilder) {
    if (event) {
      modelBuilder.remove();
      this.deselectSuggestion();
    }
  }

  selectRelationshipTypeTab(tab: RelationshipTypeTab) {
    this.suggestionsService.update({
      description: 'New suggestions tab selected',
      payload: {
        selectedTab: tab
      }
    });
  }

  async selectModelBuilderTab(relationshipId: string, tab: ModelBuilderTab) {
    const modelBuilder = await this.suggestionsService.get([
      'modelBuilder',
      relationshipId
    ]);

    modelBuilder.update({
      description: 'New tab selected',
      payload: {
        selectedTab: tab
      }
    });
  }

  deselectSuggestion() {
    this.suggestionsService.delete({
      description: 'Current suggestion deselected',
      path: ['selectedRelationship']
    });
  }

  selectSuggestion(suggestion: SuggestedRelation) {
    this.suggestionsService.update({
      description: 'New suggestions selected',
      payload: {
        selectedRelationship: suggestion.id
      }
    });
  }

  trackByFn(index: number) {
    return index;
  }
}
