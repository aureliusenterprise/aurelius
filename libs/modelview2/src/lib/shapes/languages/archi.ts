import { BasicShapeFunction, basicShapes, compose } from '../basic-shapes';
import { ConnectionStyleFunction, NodeShapeFunction } from '../types';

const group: BasicShapeFunction = (width, height) => {
  const titleBlock = `m0,0h${width / 2}v18h-${width / 2}z`;

  const mainBlock = `m0,18h${width}v${height - 18}h-${width}z`;

  return titleBlock + mainBlock;
};

const label: NodeShapeFunction = (node) => {
  const BorderType = {
    DOGEAR: 0,
    RECTANGLE: 1,
    NONE: 2,
  };

  const { height, width, style } = node;

  function getLabelShape() {
    switch (style.borderType) {
      case BorderType.DOGEAR:
        return `m0,0h${width}v${height - 18}l-18, 18h-${width - 18}z`;
      case BorderType.RECTANGLE:
      case BorderType.NONE:
        return basicShapes.rectangle(height, width);
    }
  }

  const shape = getLabelShape();

  return { shape, showIcon: false, showName: true };
};

type ArchiTypes =
  | 'ar3_Container'
  | 'ar3_Element'
  | 'ar3_Label'
  | 'ar3_ArchiDiagramModelReference';

export const archiClasses: {
  [key in ArchiTypes]?: string;
} = {
  ar3_ArchiDiagramModelReference: 'link',
};

export const archiElements: {
  [key in ArchiTypes]: NodeShapeFunction;
} = {
  ar3_ArchiDiagramModelReference: compose(basicShapes.rectangle),
  ar3_Container: compose(group, { showIcon: false }),
  ar3_Element: compose(basicShapes.rectangle, { showIcon: false }),
  ar3_Label: label,
};

export const archiRelations: {
  [key: string]: ConnectionStyleFunction;
} = {
  ar3_Line: () => ({}),
};
