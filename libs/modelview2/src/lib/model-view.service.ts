import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { defaultIfFalsy, SubType, untilDestroyed } from '@models4insight/utils';
import { Dictionary, findKey } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from './model-explorer.service';
import { ModelView, ModelViewConnection, ModelViewNode } from './parsers';
import { defs } from './shapes/defs';
import { RelationDef } from './shapes/types';

export interface ModelviewStoreContext {
  readonly defs?: Dictionary<RelationDef>;
  readonly isBuildingDefs?: boolean;
  readonly isCalculatingMinimumCoordinates?: boolean;
  readonly isSelectingView?: boolean;
  readonly minX?: number;
  readonly minY?: number;
  readonly viewId?: string;
}

const defaultState: ModelviewStoreContext = {
  defs: defs,
};

@Injectable()
export class ModelviewService extends BasicStore<ModelviewStoreContext> {
  constructor(private readonly modelExplorerService: ModelExplorerService) {
    super({ defaultState });
    this.init();
  }

  private init() {
    // Reflect the url parameter 'view' in the store
    combineLatest([
      this.select('viewId', { includeFalsy: true }),
      this.modelExplorerService.select('views'),
    ])
      .pipe(
        switchMap(([viewId, views]) => this.handleSelectView(views, viewId)),
        untilDestroyed(this)
      )
      .subscribe();

    this.nodes
      .pipe(
        switchMap((nodes) => this.handleCalculateMinimumCoordinates(nodes)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  deselectCurrentView() {
    this.viewId = null;
  }

  get connections(): Observable<ModelViewConnection[]> {
    return this.select('viewId', { includeFalsy: true }).pipe(
      switchMap((id) =>
        this.modelExplorerService.select(['views', id, 'connections'], {
          includeFalsy: true,
        })
      ),
      defaultIfFalsy({}),
      map(Object.values)
    );
  }

  get description(): Observable<string> {
    return this.select('viewId', { includeFalsy: true }).pipe(
      switchMap((id) =>
        this.modelExplorerService.select(['views', id, 'description'], {
          includeFalsy: true,
        })
      )
    );
  }

  get displayName(): Observable<string> {
    return this.select('viewId', { includeFalsy: true }).pipe(
      switchMap((id) =>
        this.modelExplorerService.select(['views', id, 'name'], {
          includeFalsy: true,
        })
      )
    );
  }

  get minX(): Observable<number> {
    return this.nodes.pipe(
      map((nodes) => {
        const x = nodes.map((node) => node.x);
        return Math.min(...x);
      })
    );
  }

  get minY(): Observable<number> {
    return this.nodes.pipe(
      map((nodes) => {
        const y = nodes.map((node) => node.y);
        return Math.min(...y);
      })
    );
  }

  get nodes(): Observable<ModelViewNode[]> {
    return this.select('viewId', { includeFalsy: true }).pipe(
      switchMap((id) =>
        this.modelExplorerService.select(['views', id, 'nodes'], {
          includeFalsy: true,
        })
      ),
      defaultIfFalsy({}),
      map(Object.values)
    );
  }

  get view() {
    return this.select('viewId', { includeFalsy: true }).pipe(
      switchMap((id) => this.modelExplorerService.select(['views', id]))
    );
  }

  set viewId(viewId: string) {
    this.update({
      description: `Selected view ${viewId}`,
      payload: { viewId },
    });
  }

  @ManagedTask('Calculating the minimum bounds of the view', { isQuiet: true })
  @MonitorAsync('isCalculatingMinimumCoordinates')
  private async handleCalculateMinimumCoordinates(nodes: ModelViewNode[]) {
    function getMinForProperty(
      propertyName: keyof SubType<(typeof nodes)[0], number>
    ) {
      const coordinates = nodes.map((node) => node[propertyName]);
      return Math.min(...coordinates);
    }

    const minX = getMinForProperty('x'),
      minY = getMinForProperty('y');

    this.update({
      description: 'New minimum coordinates available',
      payload: { minX, minY },
    });
  }

  /**
   * Selects a default view if either of the following is `true`:
   * - No view is currently selected, or
   * - The selected view is not in the model
   */
  @ManagedTask('Selecting a view', { isQuiet: true })
  @MonitorAsync('isSelectingView')
  private async handleSelectView(
    viewsById: Dictionary<ModelView>,
    viewId: string
  ) {
    // If no view is selected, or the selected view is not known, select a default view instead
    if (!(viewId && viewId in viewsById)) {
      const defaultView = findKey(viewsById);
      if (defaultView) {
        this.viewId = defaultView;
      } else {
        this.delete({
          description: 'No view selected and no default view available',
          path: ['viewId'],
        });
      }
    } else {
      this.viewId = viewId;
    }
  }
}
