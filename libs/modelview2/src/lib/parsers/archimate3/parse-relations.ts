import { indexByProperty } from '@models4insight/utils';
import { parseRelation } from './parse-relation';
import { ModelRelation } from '../types';
import { Dictionary } from 'lodash';

export async function parseRelations(
  jsonRelations: any[]
): Promise<Dictionary<ModelRelation>> {
  const parsedRelations = await Promise.all(jsonRelations.map(parseRelation));
  return indexByProperty(parsedRelations, 'id');
}
