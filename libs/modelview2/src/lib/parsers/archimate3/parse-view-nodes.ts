import { indexByProperty, Stream } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { ModelViewNode } from '../types';
import { parseViewNode } from './parse-view-node';

export async function parseViewNodes(
  nodes: Iterable<any> = []
): Promise<Dictionary<ModelViewNode>> {
  const parsedNodes = await Promise.all(Stream.from(nodes).map(parseViewNode));
  return indexByProperty(parsedNodes, 'id');
}
