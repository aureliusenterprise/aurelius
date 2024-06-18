import { decodeXML } from '@models4insight/utils';
import { ModelView } from '../types';
import { getProperties } from './get-properties';
import { getViewNodes } from './get-view-nodes';
import { parseViewConnections } from './parse-view-connections';
import { parseViewNodes } from './parse-view-nodes';

export async function parseView(view: any): Promise<ModelView> {
  const id = view['@identifier'],
    name = decodeXML(view['ar3_name']?.[0]['value']),
    description = decodeXML(view['ar3_documentation']?.['value']);

  const nodes = getViewNodes(view),
    connections = view['ar3_connection'] ?? [];

  const [properties, parsedNodes, parsedConnections] = await Promise.all([
    Promise.resolve(view).then(getProperties),
    parseViewNodes(nodes),
    parseViewConnections(connections),
  ]);

  return {
    id,
    name,
    description,
    properties,
    nodes: parsedNodes,
    connections: parsedConnections,
    type: 'ar3_View',
    humanReadableType: 'View',
    parserType: 'view',
  };
}
