import { Dictionary } from 'lodash';
import { basicShapes, compose } from '../basic-shapes';
import { ConnectionStyleFunction, NodeShapeFunction } from '../types';

export const lineageClasses: Dictionary<string> = {
  lineage_dataset: 'dataset',
  lineage_process: 'process',
};

export const lineageElements: Dictionary<NodeShapeFunction> = {
  lineage_dataset: compose(basicShapes.rectangle),
  lineage_process: compose(basicShapes.rectangle),
};

export const lineageRelations: Dictionary<ConnectionStyleFunction> = {
  lineage_relation: () => ({
    'marker-end': 'generic-arrow',
  }),
};
