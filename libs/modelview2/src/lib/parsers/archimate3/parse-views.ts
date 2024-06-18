import { indexByProperty } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { ModelView } from '../types';
import { parseView } from './parse-view';

export async function parseViews(
  jsonViews: any[] = []
): Promise<Dictionary<ModelView>> {
  const parsedViews = await Promise.all(jsonViews.map(parseView));
  return indexByProperty(parsedViews, 'id');
}
