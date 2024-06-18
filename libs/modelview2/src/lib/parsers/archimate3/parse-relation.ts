import { archimate3 } from '@models4insight/metamodel';
import { decodeXML } from '@models4insight/utils';
import { ModelRelation } from '../types';
import { getProperties } from './get-properties';

const humanReadableTypes: {
  [key in keyof typeof archimate3.relations_by_tag]: string;
} = {
  ar3_Access: 'Accesses',
  ar3_Aggregation: 'Aggregates',
  ar3_Assignment: 'Assigned to',
  ar3_Association: 'Associated with',
  ar3_Composition: 'Composes',
  ar3_Flow: 'Flows into',
  ar3_Influence: 'Influences',
  ar3_Realization: 'Realizes',
  ar3_Serving: 'Serves',
  ar3_Specialization: 'Specializes',
  ar3_Triggering: 'Triggers',
  lineage_relation: 'Flows into',
};

export async function parseRelation(jsonRelation: any): Promise<ModelRelation> {
  const id = jsonRelation['@identifier'],
    source = jsonRelation['@source'],
    target = jsonRelation['@target'],
    type = jsonRelation['@xsi_type'];

  const description = decodeXML(jsonRelation['ar3_documentation']?.['value']),
    name = decodeXML(jsonRelation['ar3_name']?.[0]['value']),
    displayName = humanReadableTypes[type],
    humanReadableType = archimate3.relations_by_tag[type];

  const options = {};

  if (type === 'ar3_Access') {
    options['accessType'] = jsonRelation['@accessType'];
  }

  if (type === 'ar3_Association') {
    options['isDirected'] = jsonRelation['@isDirected'];
  }

  const properties = getProperties(jsonRelation);

  return {
    id,
    source,
    target,
    type,
    description,
    name,
    displayName,
    humanReadableType,
    options,
    properties,
    parserType: 'relationship',
  };
}
