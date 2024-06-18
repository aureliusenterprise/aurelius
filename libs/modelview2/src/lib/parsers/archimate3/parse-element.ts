import { archimate3 } from '@models4insight/metamodel';
import { decodeXML } from '@models4insight/utils';
import { ModelElement } from '../types';
import { getProperties } from './get-properties';

export async function parseElement(jsonElement: any): Promise<ModelElement> {
  const id = jsonElement['@identifier'],
    type = jsonElement['@xsi_type'];

  const description = decodeXML(jsonElement['ar3_documentation']?.['value']),
    humanReadableType = archimate3.elements[type],
    name = decodeXML(jsonElement['ar3_name']?.[0]['value']);

  const properties = getProperties(jsonElement);

  return {
    id,
    description,
    humanReadableType,
    name,
    properties,
    type,
    parserType: 'element',
  };
}
