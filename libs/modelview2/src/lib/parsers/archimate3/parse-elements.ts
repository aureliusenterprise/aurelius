import { indexByProperty } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { ModelElement } from '../types';
import { parseElement } from './parse-element';

export async function parseElements(
  jsonElements: any[] = []
): Promise<Dictionary<ModelElement>> {
  const parsedElements = await Promise.all(jsonElements.map(parseElement));
  return indexByProperty(parsedElements, 'id');
}
