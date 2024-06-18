import { NodeShapeFunction } from './types';

type BasicShape =
  | 'ellipse'
  | 'octagon'
  | 'parallelogram'
  | 'rectangle'
  | 'roundedRectangle';

export type BasicShapeFunction = (width: number, height: number) => string;

export interface ComposeShapeOptions {
  readonly showIcon?: boolean;
  readonly showName?: boolean;
}

export function compose(
  basicShape: BasicShapeFunction,
  { showIcon = true, showName = true }: ComposeShapeOptions = {}
): NodeShapeFunction {
  return ({ width = 0, height = 0 }) => ({
    shape: basicShape(width, height),
    showIcon,
    showName,
  });
}

export const basicShapes: { [key in BasicShape]: BasicShapeFunction } = {
  ellipse: (width, height) =>
    `m0,0a${width / 2},${height / 2},0,0,0,${width},${height}a${width / 2},${
      height / 2
    },0,0,0,-${width},-${height}z`,
  octagon: (width, height) =>
    `m12,0h${width - 24}l12,12v${height - 24}l-12,12h-${width - 24}l-12,-12v-${
      height - 24
    }l12,-12z`,
  parallelogram: (width, height) =>
    `m${width * 0.1},0h${width * 0.9}l-${width * 0.1},${height}h${
      width * 0.9
    },0z`,
  rectangle: (width, height) => `m0,0h${width}v${height}h-${width}z`,
  roundedRectangle: (width, height) =>
    `m12,0h${width - 24}a12,12,0,0,1,12,12v${height - 24}a12,12,0,0,1,-12,12h-${
      width - 24
    }a12,12,0,0,1,-12,-12v-${height - 24}a12,12,0,0,1,12,-12z`,
};
