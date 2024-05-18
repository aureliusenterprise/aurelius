import { Injectable, OnDestroy } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { ModelService, ModelDataService } from '@models4insight/services/model';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { of } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { FlaskService } from '../../api/flask.service';
import { ExtractorService } from '../extractor.service';
import { ModelBuilder } from './model-builder';

export type RelationshipTypeTab = 'dynamic' | 'structural' | 'other';

export interface SuggestionsStoreContext {
  readonly currentPreviewModel?: any;
  readonly isCalculatingBijacencyMap?: boolean;
  readonly isGeneratingPreviewModel?: boolean;
  readonly isUpdatingModelRules?: boolean;
  readonly isUpdatingViewRules?: boolean;
  readonly modelBuilder?: Dictionary<ModelBuilder>;
  readonly selectedRelationship?: string;
  readonly selectedTab?: RelationshipTypeTab;
}

const suggestionsServiceDefaultState: SuggestionsStoreContext = {
  isUpdatingModelRules: false,
  isUpdatingViewRules: false,
  selectedTab: 'dynamic'
};

// TODO: Add Angular decorator.
@Injectable()
export class SuggestionsService extends BasicStore<SuggestionsStoreContext>
  implements OnDestroy {
  constructor(
    private modelService: ModelService,
    private modelDataService: ModelDataService,
    private extractorService: ExtractorService,
    private flaskApi: FlaskService,
    storeService: StoreService
  ) {
    super({
      defaultState: suggestionsServiceDefaultState,
      name: 'SuggestionsService',
      storeService
    });
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    // Whenever the dataset changes, reset
    this.extractorService
      .select('currentDataset')
      .pipe(untilDestroyed(this))
      .subscribe(() => this.reset());

    // Whenever a relationship is selected
    // and there is no model builder context for that relationship yet,
    // initialize the model builder context
    this.select('selectedRelationship')
      .pipe(
        switchMap(id =>
          of(id).pipe(
            switchMap(() => this.initializeModelBuilder(id)),
            takeUntil(this.select(['modelBuilder', id]))
          )
        ),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the active model builder changes, update the model service with the associated preview model
    this.select('selectedRelationship')
      .pipe(
        switchMap(id => this.select(['modelBuilder', id])),
        switchMap(modelBuilder => modelBuilder.select('previewModel')),
        untilDestroyed(this)
      )
      .subscribe(previewModel => (this.modelService.model = previewModel));

      this.select('selectedRelationship')
      .pipe(
        switchMap(id => this.select(['modelBuilder', id])),
        switchMap(modelBuilder => modelBuilder.select('previewData')),
        untilDestroyed(this)
      )
      .subscribe(previewData => (this.modelDataService.dataByConceptId = previewData));
  }

  private async initializeModelBuilder(id: string) {
    const modelBuilder = new ModelBuilder(
      id,
      this.extractorService,
      this.flaskApi,
      this
    );
    this.update({
      description: `Initialized model builder context for sugggestion ${id}`,
      path: ['modelBuilder', id],
      payload: modelBuilder
    });
  }
}
