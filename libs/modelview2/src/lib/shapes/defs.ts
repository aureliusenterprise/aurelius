import { Dictionary } from 'lodash';
import { ar3RelationDef } from './languages';
import { RelationDef } from './types';

export const defs: Dictionary<RelationDef> = {
  ...ar3RelationDef,
};
