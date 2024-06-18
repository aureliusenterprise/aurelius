import { KeyValue } from '@angular/common';
import {
  Component,
  Inject,
  InjectionToken,
  OnInit,
  Optional,
} from '@angular/core';
import { faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { SortableTableShellConfig } from '@models4insight/components';
import { ModelDataService } from '@models4insight/services/model';
import { Dictionary, identity } from 'lodash';
import { combineLatest, Observable, of } from 'rxjs';
import { map, shareReplay, switchMap } from 'rxjs/operators';
import { ColorViewService } from '../../color-view.service';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelviewService } from '../../model-view.service';
import { ModelEntity, ModelView } from '../../parsers';

export const MODEL_BROWSER_SELECTION_ADDONS = new InjectionToken<
  typeof Component
>('MODEL_BROWSER_SELECTION_ADDONS');

const propertiesTableConfig: SortableTableShellConfig<
  KeyValue<string, string>
> = {
  key: { displayName: 'Name', description: 'The name of the property' },
  value: { displayName: 'Value', description: 'The value of the property' },
};

const viewsTableConfig: SortableTableShellConfig<ModelEntity> = {
  name: { displayName: 'Name', description: 'The name of the view' },
  description: {
    displayName: 'Description',
    description: 'The view documentation',
    truncate: 'end',
  },
};

@Component({
  selector: 'models4insight-model-browser-selection',
  templateUrl: 'selection.component.html',
  styleUrls: ['selection.component.scss'],
})
export class ModelBrowserSelectionComponent implements OnInit {
  readonly propertiesTableConfig = propertiesTableConfig;
  readonly viewsTableConfig = viewsTableConfig;

  readonly faArrowRight = faArrowRight;

  properties$: Observable<Dictionary<any>>;
  selectedEntityColor$: Observable<string>;
  selectedEntityColorBucket$: Observable<string>;
  referencedConcepts$: Observable<ModelEntity[]>;
  referencingConcepts$: Observable<ModelEntity[]>;
  referencingViews$: Observable<ModelView[]>;
  selectedEntity$: Observable<ModelEntity>;
  selectedEntityId$: Observable<string>;
  selectedView$: Observable<ModelView>;

  constructor(
    @Optional()
    @Inject(MODEL_BROWSER_SELECTION_ADDONS)
    readonly addons: Dictionary<typeof Component>,
    private readonly colorViewService: ColorViewService,
    private readonly modelDataService: ModelDataService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {}

  ngOnInit() {
    this.selectedView$ = this.modelviewService.select('viewId').pipe(
      switchMap((id) => this.modelExplorerService.select(['views', id])),
      shareReplay()
    );

    this.selectedEntityId$ = this.modelExplorerService
      .select('selectedEntity', { includeFalsy: true })
      .pipe(shareReplay());

    this.selectedEntity$ = this.selectedEntityId$.pipe(
      switchMap((id) =>
        this.modelExplorerService.select(['entitiesById', id], {
          includeFalsy: true,
        })
      ),
      shareReplay()
    );

    const selectedEntityData$ = this.selectedEntityId$.pipe(
      switchMap((id) =>
        this.modelDataService.select(['dataByConceptId', id], {
          includeFalsy: true,
        })
      )
    );

    this.properties$ = combineLatest([
      this.selectedEntity$,
      selectedEntityData$,
    ]).pipe(
      map(([entity, data = {}]) => {
        const properties =
          entity && 'properties' in entity ? entity.properties : {};
        return { ...properties, ...data };
      })
    );

    const selectEntitiesById = (ids: string[] = []) => {
      const views = combineLatest(
        ids.map((id) =>
          this.modelExplorerService.select(['entitiesById', id], {
            includeFalsy: true,
          })
        )
      ).pipe(map((entities) => entities.filter(identity)));
      return ids.length ? views : of([]);
    };

    this.referencedConcepts$ = this.modelExplorerService
      .select('selectedEntity')
      .pipe(
        switchMap((id) =>
          this.modelExplorerService
            .select(['conceptsByRelationId', id], { includeFalsy: true })
            .pipe(switchMap(selectEntitiesById))
        )
      );

    this.referencingConcepts$ = this.modelExplorerService
      .select('selectedEntity')
      .pipe(
        switchMap((id) =>
          this.modelExplorerService
            .select(['relationsByConceptId', id], { includeFalsy: true })
            .pipe(switchMap(selectEntitiesById))
        )
      );

    this.referencingViews$ = this.modelExplorerService
      .select('selectedEntity')
      .pipe(
        switchMap((id) =>
          this.modelExplorerService
            .select(['viewsByEntityId', id], { includeFalsy: true })
            .pipe(switchMap(selectEntitiesById))
        )
      );
  }

  deselectEntity() {
    this.modelExplorerService.deleteConceptSelection();
  }

  deselectView() {
    this.modelviewService.deselectCurrentView();
  }

  updateLegendColor(bucket: string, color: string) {
    this.colorViewService.update({
      description: `Legend color set to ${color} for bucket ${bucket}`,
      path: ['legend', bucket],
      payload: color,
    });
  }

  selectEntity(entity: ModelEntity) {
    this.modelExplorerService.selectedEntity = entity.id;
  }

  selectView(view: ModelView) {
    this.modelviewService.viewId = view.id;
  }
}
