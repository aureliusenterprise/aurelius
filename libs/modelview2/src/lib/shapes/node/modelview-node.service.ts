import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Subject } from 'rxjs';
import { map, switchMap, switchMapTo, take } from 'rxjs/operators';
import { ColorViewService } from '../../color-view.service';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelviewService } from '../../model-view.service';
import { ModelElement, ModelViewNode } from '../../parsers';
import { getShapeForType } from '../get-shape-for-type';

export interface ModelviewNodeStoreContext {
  readonly viewNode?: ModelViewNode;
  readonly modelNode?: ModelElement;
}

function formatPosition(x = 0, y = 0, minX = 0, minY = 0): string {
  return `translate(${x - minX}, ${y - minY})`;
}

@Injectable()
export class ModelviewNodeService extends BasicStore<ModelviewNodeStoreContext> {
  private readonly loadDetails$ = new Subject<void>();

  constructor(
    private readonly colorViewService: ColorViewService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {
    super();
    this.init();
  }

  private init() {
    this.select(['viewNode', 'ref'])
      .pipe(
        switchMap((id) => this.modelExplorerService.select(['elements', id])),
        untilDestroyed(this)
      )
      .subscribe((modelNode) =>
        this.update({
          description: 'Model node definition updated',
          payload: { modelNode },
        })
      );
  }

  async selectNode() {
    const { id, ref } = await this.get('viewNode');
    this.modelExplorerService.selectedEntity = ref ?? id;
  }

  get color() {
    return combineLatest([
      this.select(['viewNode', 'style', 'fillColor'], { includeFalsy: true }),
      this.select(['viewNode', 'id']).pipe(
        switchMap((id) => this.colorViewService.getColorById(id))
      ),
      this.select(['modelNode', 'id'], { includeFalsy: true }).pipe(
        switchMap((id) => this.colorViewService.getColorById(id))
      ),
    ]).pipe(
      map(
        ([fillColor, viewNodeColor, modelNodeColor]) =>
          viewNodeColor ?? modelNodeColor ?? fillColor
      )
    );
  }

  get displayName() {
    return combineLatest([
      this.select(['modelNode', 'name'], { includeFalsy: true }),
      this.select(['viewNode', 'name'], { includeFalsy: true }),
    ]).pipe(
      map(
        ([conceptName, viewElementName]) => conceptName ?? viewElementName ?? ''
      )
    );
  }

  get position() {
    return combineLatest([
      this.select(['viewNode', 'x'], { includeFalsy: true }),
      this.select(['viewNode', 'y'], { includeFalsy: true }),
      this.modelviewService.select('minX', { includeFalsy: true }),
      this.modelviewService.select('minY', { includeFalsy: true }),
    ]).pipe(map(([x, y, minX, minY]) => formatPosition(x, y, minX, minY)));
  }

  get shape() {
    return combineLatest([this.type, this.select('viewNode')]).pipe(
      map(([type, node]) => {
        const shape = getShapeForType(type);
        if (!shape) {
          console.log(type);
        }
        return shape(node);
      })
    );
  }

  get type() {
    return combineLatest([
      this.select(['viewNode', 'type']),
      this.select(['modelNode', 'type'], { includeFalsy: true }),
    ]).pipe(map(([viewType, modelType]) => modelType ?? viewType));
  }

  set viewNode(viewNode: ModelViewNode) {
    this.update({
      description: 'View node definition updated',
      payload: { viewNode },
    });
  }
}
