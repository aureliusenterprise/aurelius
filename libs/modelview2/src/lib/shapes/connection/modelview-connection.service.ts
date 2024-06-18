import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { pairwise, untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ColorViewService } from '../../color-view.service';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelviewService } from '../../model-view.service';
import {
  ModelRelation,
  ModelViewConnection,
  ModelViewConnectionBendpoint,
  ModelViewNode,
} from '../../parsers';
import { getRelationForType } from '../get-shape-for-type';

export interface ModelviewConnectionStoreContext {
  readonly isCalculatingPath?: boolean;
  readonly modelRelation?: ModelRelation;
  readonly path?: string;
  readonly transform?: string;
  readonly viewConnection?: ModelViewConnection;
}

function areNested(source: ModelViewNode, target: ModelViewNode) {
  function isNested(
    { x: x1, y: y1, width: width1, height: height1 }: ModelViewNode,
    { x: x2, y: y2, width: width2, height: height2 }: ModelViewNode
  ) {
    return (
      x1 >= x2 &&
      x1 + width1 <= x2 + width2 &&
      y1 >= y2 &&
      y1 + height1 <= y2 + height2
    );
  }

  return isNested(source, target) || isNested(target, source);
}

function findMiddlePoint([...path]: Iterable<PointToPoint>): PointOnPath {
  const point = path[Math.floor(path.length / 2)];
  if (path.length % 2) {
    return { x: point.x1, y: point.y1 };
  } else {
    return {
      x: point.x1 + (point.x2 - point.x1) / 2,
      y: point.y1 + (point.y2 - point.y1) / 2,
    };
  }
}

function isConnection(
  obj: ModelViewNode | ModelViewConnection | ModelViewConnectionBendpoint
): obj is ModelViewConnection {
  return 'source' in obj;
}

interface PointOnPath {
  readonly x: number;
  readonly y: number;
  readonly height?: number;
  readonly width?: number;
}

interface PointToPoint {
  readonly x1: number;
  readonly x2: number;
  readonly y1: number;
  readonly y2: number;
}

function getShortestLineEndpoints(
  sourcePos: number,
  sourceSurfaceLength: number,
  targetPos: number,
  targetSurfaceLength: number
) {
  let a = 0,
    b = 0;
  //Target is completely left of source. Draw connection to the edges
  if (sourcePos > targetPos + targetSurfaceLength) {
    a = sourcePos;
    b = targetPos + targetSurfaceLength;
  }
  //Target is somewhat left of source. Center on the overlap.
  else if (
    sourcePos >= targetPos &&
    sourcePos + sourceSurfaceLength >= targetPos + targetSurfaceLength
  ) {
    a = b = sourcePos + (targetPos + targetSurfaceLength - sourcePos) / 2;
  }
  //Target is completely right of source. Draw connection to the edges
  else if (sourcePos + sourceSurfaceLength < targetPos) {
    a = sourcePos + sourceSurfaceLength;
    b = targetPos;
  }
  //Target is somewhat right of source. Center on the overlap.
  else if (
    sourcePos <= targetPos &&
    sourcePos + sourceSurfaceLength <= targetPos + targetSurfaceLength
  ) {
    a = b = targetPos + (sourcePos + sourceSurfaceLength - targetPos) / 2;
  }
  //Target is both left and right of source. Center on source
  else if (
    sourcePos > targetPos &&
    sourcePos + sourceSurfaceLength < targetPos + targetSurfaceLength
  ) {
    a = b = sourcePos + sourceSurfaceLength / 2;
  }
  //Target is neither left or right of source. Center on target.
  else {
    a = b = targetPos + targetSurfaceLength / 2;
  }

  return [a, b];
}

function pointToPoint(
  {
    x: sourceX,
    y: sourceY,
    height: sourceHeight = 0,
    width: sourceWidth = 0,
  }: PointOnPath,
  {
    x: targetX,
    y: targetY,
    height: targetHeight = 0,
    width: targetWidth = 0,
  }: PointOnPath
): PointToPoint {
  const [x1, x2] = getShortestLineEndpoints(
    sourceX,
    sourceWidth,
    targetX,
    targetWidth
  );
  const [y1, y2] = getShortestLineEndpoints(
    sourceY,
    sourceHeight,
    targetY,
    targetHeight
  );

  return { x1, x2, y1, y2 };
}

@Injectable()
export class ModelviewConnectionService extends BasicStore<ModelviewConnectionStoreContext> {
  constructor(
    private readonly colorViewService: ColorViewService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {
    super();
    this.init();
  }

  private init() {
    this.select(['viewConnection', 'ref'])
      .pipe(
        switchMap((id) => this.modelExplorerService.select(['relations', id])),
        untilDestroyed(this)
      )
      .subscribe((modelRelation) =>
        this.update({
          description: 'Model relation definition updated',
          payload: { modelRelation },
        })
      );

    this.select('viewConnection')
      .pipe(
        switchMap((connection) =>
          combineLatest([
            this.modelExplorerService.select([
              'entitiesById',
              connection.source,
            ]),
            this.modelExplorerService.select([
              'entitiesById',
              connection.target,
            ]),
          ]).pipe(
            switchMap(([source, target]) =>
              this.handleCalculatePath(
                connection,
                source as ModelViewNode | ModelViewConnection,
                target as ModelViewNode | ModelViewConnection
              )
            )
          )
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  async selectConnection() {
    const { id, ref } = await this.get('viewConnection');
    this.modelExplorerService.selectedEntity = ref ?? id;
  }

  get color() {
    return combineLatest([
      this.select(['viewConnection', 'style', 'lineColor'], {
        includeFalsy: true,
      }),
      this.select(['viewConnection', 'id']).pipe(
        switchMap((id) => this.colorViewService.getColorById(id))
      ),
      this.select(['modelRelation', 'id'], { includeFalsy: true }).pipe(
        switchMap((id) => this.colorViewService.getColorById(id))
      ),
    ]).pipe(
      map(
        ([fillColor, viewConnectionColor, modelRelationColor]) =>
          viewConnectionColor ?? modelRelationColor ?? fillColor
      )
    );
  }

  get displayName() {
    return combineLatest([
      this.select(['modelRelation', 'name'], { includeFalsy: true }),
      this.select(['viewConnection', 'name'], { includeFalsy: true }),
    ]).pipe(map(([modelName, viewName]) => modelName ?? viewName ?? ''));
  }

  get style() {
    return combineLatest([
      this.select('modelRelation', { includeFalsy: true }),
      this.select('viewConnection'),
    ]).pipe(
      map(([relation, connection]) => {
        const type = relation?.type ?? connection.type;
        const styleFunction = getRelationForType(type);
        return styleFunction ? styleFunction(connection, relation) : {};
      })
    );
  }

  set viewConnection(viewConnection: ModelViewConnection) {
    this.update({
      description: 'View connection definition updated',
      payload: { viewConnection },
    });
  }

  @MonitorAsync('isCalculatingPath')
  private async handleCalculatePath(
    viewConnection: ModelViewConnection,
    source: ModelViewNode | ModelViewConnection,
    target: ModelViewNode | ModelViewConnection
  ) {
    const [steps, minX, minY] = await Promise.all([
      this.buildPath(viewConnection, source, target),
      this.modelviewService.get('minX'),
      this.modelviewService.get('minY'),
    ]);

    if (steps && steps.length) {
      const path = `m0,0${steps
        .map((step) => `l${step.x2 - step.x1},${step.y2 - step.y1}`)
        .join('')}`;

      const transform = `translate(${steps[0].x1 - minX},${
        steps[0].y1 - minY
      })`;

      this.update({
        description: `Updated connection path`,
        payload: { path, transform },
      });
    } else {
      this.delete({
        description: `Deleted connection path`,
        path: ['path'],
      });
      this.delete({
        description: `Deleted connection transform`,
        path: ['transform'],
      });
    }
  }

  private async buildPath(
    connection: ModelViewConnection,
    source?: ModelViewNode | ModelViewConnection,
    target?: ModelViewNode | ModelViewConnection
  ) {
    if (!source) {
      source = (await this.modelExplorerService.get([
        'entitiesById',
        connection.source,
      ])) as ModelViewNode | ModelViewConnection;
    }

    if (!target) {
      target = (await this.modelExplorerService.get([
        'entitiesById',
        connection.target,
      ])) as ModelViewNode | ModelViewConnection;
    }

    if (
      isConnection(source) ||
      isConnection(target) ||
      !areNested(source, target)
    ) {
      const steps = [source, ...connection.bendpoints, target];
      return this.buildPathFromSteps(steps);
    }
  }

  private async buildPathFromSteps(
    steps: Iterable<
      ModelViewNode | ModelViewConnection | ModelViewConnectionBendpoint
    >
  ) {
    const result: PointToPoint[] = [];
    for (let [from, to] of pairwise(steps)) {
      if (isConnection(from)) {
        const fromPath = await this.buildPath(from);
        from = findMiddlePoint(fromPath);
      }
      if (isConnection(to)) {
        const toPath = await this.buildPath(to);
        to = findMiddlePoint(toPath);
      }
      result.push(pointToPoint(from, to));
    }
    return result;
  }
}
