import { rgbToHex } from '@models4insight/utils';
import { ModelViewConnection, ModelViewConnectionBendpoint } from '../types';

const humanReadableTypes = {
  ar3_Line: 'Connection',
};

function parseBendpoint(bendpoint: any): ModelViewConnectionBendpoint {
  return {
    x: Number.parseFloat(bendpoint['@x']),
    y: Number.parseFloat(bendpoint['@y']),
  };
}

function parseBendpoints(bendpoints: any[] = []) {
  return bendpoints.map(parseBendpoint);
}

export async function parseViewConnection(
  view_connection: any
): Promise<ModelViewConnection> {
  const id = view_connection['@identifier'],
    ref = view_connection['@relationshipRef'],
    source = view_connection['@source'],
    target = view_connection['@target'],
    type = view_connection['@xsi_type'],
    humanReadableType = humanReadableTypes[type];

  const bendpoints = parseBendpoints(view_connection['ar3_bendpoint']);

  const styleOptions = {};

  if ('ar3_style' in view_connection) {
    const styles = view_connection['ar3_style'];
    if ('ar3_lineColor' in styles) {
      const lineColor = styles['ar3_lineColor'];
      styleOptions['lineColor'] = rgbToHex(
        Number.parseInt(lineColor['@r'], 10),
        Number.parseInt(lineColor['@g'], 10),
        Number.parseInt(lineColor['@b'], 10)
      );
    }
  }

  return {
    id,
    ref,
    source,
    target,
    type,
    humanReadableType,
    bendpoints,
    style: styleOptions,
    parserType: 'connection',
  };
}
