import { indexByProperty } from '@models4insight/utils';
import { parseViewConnection } from './parse-view-connection';
import { Dictionary } from 'lodash';
import { ModelViewConnection } from '../types';

export async function parseViewConnections(
  connections: any[] = []
): Promise<Dictionary<ModelViewConnection>> {
  const parsedConnections = await Promise.all(
    connections.map(parseViewConnection)
  );
  return indexByProperty(parsedConnections, 'id');
}
