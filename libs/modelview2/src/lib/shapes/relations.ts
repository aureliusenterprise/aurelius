import { Dictionary } from 'lodash';
import { ar3Relations, archiRelations, lineageRelations } from './languages';
import { ConnectionStyleFunction } from './types';

export const relations: Dictionary<ConnectionStyleFunction> = {
  ...ar3Relations,
  ...archiRelations,
  ...lineageRelations,
};
