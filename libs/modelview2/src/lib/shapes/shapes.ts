import { Dictionary } from 'lodash';
import { ar3Elements, archiElements, lineageElements } from './languages';
import { NodeShapeFunction } from './types';

export const shapes: Dictionary<NodeShapeFunction> = {
  ...archiElements,
  ...ar3Elements,
  ...lineageElements,
};
