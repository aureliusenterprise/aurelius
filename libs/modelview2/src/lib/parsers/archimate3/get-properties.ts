import { decodeXML } from '@models4insight/utils';
import { ModelProperties } from '../types';

/**
 * Parses the properties of the given concept and returns them as a dictionary
 * @param concept The concept for which to retrieve the properties
 */
export function getProperties(concept: any): ModelProperties {
  const jsonProperties = concept['ar3_properties']?.['ar3_property'] ?? [],
    properties = {};
  for (const property of jsonProperties) {
    const propertyName = decodeXML(property['@propertyDefinitionRef']),
      propertyValue = decodeXML(property['ar3_value']['value']);

    properties[propertyName] = propertyValue;
  }
  return properties;
}
