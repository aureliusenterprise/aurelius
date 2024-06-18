import { ModelParserResult } from '../types';
import { parseElements } from './parse-elements';
import { parseOrganizations } from './parse-organizations';
import { parseRelations } from './parse-relations';
import { parseViews } from './parse-views';

export async function parseModel(jsonModel: any): Promise<ModelParserResult> {
  const model = jsonModel['ar3_model'];

  const info = {
    name: model['ar3_name']?.[0]['value'] ?? 'ArchiMate Model',
  };

  const jsonElements = model['ar3_elements']?.['ar3_element'],
    jsonRelations = model['ar3_relationships']?.['ar3_relationship'],
    jsonViews = model['ar3_views']?.['ar3_diagrams']['ar3_view'],
    jsonOrganizations = model['ar3_organizations']?.[0]['ar3_item'];

  const [elements, relations, views, organizations] = await Promise.all([
    parseElements(jsonElements),
    parseRelations(jsonRelations),
    parseViews(jsonViews),
    parseOrganizations(jsonOrganizations),
  ]);

  return {
    info,
    elements,
    relations,
    views,
    organizations,
  };
}
