import { validateRequiredArguments } from '@models4insight/utils';
import { Classification, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/entity/guid';

/**
 * Returns the details for a classification given the `classificationName` as well as the `entityGuid` of the associated entity.
 * @param entityGuid the unique id of the associated entity
 * @param classificationName the type name of the classification
 */
export function getClassificationForEntity(
  entityGuid: string,
  classificationName: string,
  { forceUpdate = false }: GetOptions = {}
) {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getClassificationForEntity');

  const path = `${BASE_PATH}/${entityGuid}/classification/${classificationName}`;

  return http.cache(forceUpdate).get<Classification>(path);
}
