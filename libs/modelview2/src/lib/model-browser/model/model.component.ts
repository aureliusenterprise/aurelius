import { Component, OnInit, ViewChild } from '@angular/core';
import {
  FuzzySearchInputComponent,
  FuzzySearchTokenizerConfig,
} from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { shareReplay, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelElement, ModelEntity, ModelRelation } from '../../parsers';
import { ModelBrowserModelService } from './model.service';

const modelEntityTokenizerConfig: FuzzySearchTokenizerConfig<
  ModelElement | ModelRelation
> = {
  id: { static: true },
  name: {},
  description: {},
  displayName: {},
  humanReadableType: {},
};

@Component({
  selector: 'models4insight-model-browser-model',
  templateUrl: 'model.component.html',
  styleUrls: ['model.component.scss'],
  providers: [ModelBrowserModelService],
})
export class ModelBrowserModelComponent implements OnInit {
  elements$: Observable<ModelElement[]>;
  relationships$: Observable<ModelRelation[]>;
  selectedEntity$: Observable<ModelEntity>;

  constructor(
    private readonly modelBrowserModelService: ModelBrowserModelService,
    private readonly modelExplorerService: ModelExplorerService
  ) {}

  ngOnInit() {
    this.elements$ = this.modelBrowserModelService.select('suggestedElements');

    this.relationships$ =
      this.modelBrowserModelService.select('suggestedRelations');

    this.selectedEntity$ = this.modelExplorerService
      .select('selectedEntity', { includeFalsy: true })
      .pipe(
        switchMap((id) =>
          this.modelExplorerService.select(['entitiesById', id])
        ),
        shareReplay()
      );
  }

  deselectEntity() {
    this.modelExplorerService.deleteConceptSelection();
  }

  selectEntity(entity: ModelEntity) {
    this.modelExplorerService.selectedEntity = entity.id;
  }

  @ViewChild(FuzzySearchInputComponent, { static: true })
  set searchInput(searchInput: FuzzySearchInputComponent<ModelEntity>) {
    if (searchInput) {
      searchInput.tokenizerConfig = modelEntityTokenizerConfig;

      this.modelBrowserModelService.searchItems
        .pipe(untilDestroyed(searchInput))
        .subscribe((items) => (searchInput.searchItems = items));

      searchInput.suggestionsChanged
        .pipe(untilDestroyed(searchInput))
        .subscribe((suggestions) =>
          this.modelBrowserModelService.update({
            description: 'New suggestions available',
            payload: { suggestions },
          })
        );
    }
  }
}
