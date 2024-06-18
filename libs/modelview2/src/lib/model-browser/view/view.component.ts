import { KeyValue } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { Dictionary, identity } from 'lodash';
import { combineLatest, Observable, of } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ColorViewService } from '../../color-view.service';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelviewService } from '../../model-view.service';
import { ModelView } from '../../parsers';

const legendTableConfig: SortableTableShellConfig<KeyValue<string, string>> = {
  key: {
    displayName: 'Category',
    description: 'The name of the category',
  },
  value: {
    displayName: 'Color',
    description:
      'Concepts in the view with this color belong to the corresponding category',
    isNarrow: true,
  },
};

const propertiesTableConfig: SortableTableShellConfig<
  KeyValue<string, string>
> = {
  key: { displayName: 'Name', description: 'The name of the property' },
  value: { displayName: 'Value', description: 'The value of the property' },
};

const viewsTableConfig: SortableTableShellConfig<ModelView> = {
  name: { displayName: 'Name', description: 'The name of the view' },
  description: {
    displayName: 'Description',
    description: 'The view documentation',
    truncate: 'end',
  },
};

@Component({
  selector: 'models4insight-model-browser-view',
  templateUrl: 'view.component.html',
  styleUrls: ['view.component.scss'],
})
export class ModelBrowserViewComponent implements OnInit {
  readonly legendTableConfig = legendTableConfig;
  readonly propertiesTableConfig = propertiesTableConfig;
  readonly viewsTableConfig = viewsTableConfig;

  isPalletteFixed$: Observable<boolean>;
  legend$: Observable<Dictionary<string>>;
  referencedViews$: Observable<ModelView[]>;
  referencingViews$: Observable<ModelView[]>;
  selectedView$: Observable<ModelView>;
  selectedViewId$: Observable<string>;

  constructor(
    private readonly colorViewService: ColorViewService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {}

  ngOnInit() {
    this.isPalletteFixed$ = this.colorViewService.select('isPalletteFixed');
    this.legend$ = this.colorViewService.select('legend');
    this.selectedView$ = this.modelviewService.view;
    this.selectedViewId$ = this.modelviewService.select('viewId', {
      includeFalsy: true,
    });

    const selectViewsById = (ids: string[] = []) => {
      const views = combineLatest(
        ids.map((id) =>
          this.modelExplorerService.select(['views', id], {
            includeFalsy: true,
          })
        )
      ).pipe(map((views) => views.filter(identity)));
      return ids.length ? views : of([]);
    };

    this.referencedViews$ = this.modelviewService
      .select('viewId')
      .pipe(
        switchMap((id) =>
          this.modelExplorerService
            .select(['entitiesByViewId', id], { includeFalsy: true })
            .pipe(switchMap(selectViewsById))
        )
      );

    this.referencingViews$ = this.modelviewService
      .select('viewId')
      .pipe(
        switchMap((id) =>
          this.modelExplorerService
            .select(['viewsByEntityId', id], { includeFalsy: true })
            .pipe(switchMap(selectViewsById))
        )
      );
  }

  deselectView() {
    this.modelviewService.deselectCurrentView();
  }

  selectView(view: ModelView) {
    this.modelviewService.viewId = view.id;
  }

  updateLegendColor(bucket: string, color: string) {
    this.colorViewService.update({
      description: `Legend color set to ${color} for bucket ${bucket}`,
      path: ['legend', bucket],
      payload: color,
    });
  }
}
