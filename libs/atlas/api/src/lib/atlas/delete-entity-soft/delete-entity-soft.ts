import { validateRequiredArguments } from '@models4insight/utils';
import { EntityMutationResponse } from '../../types';
import { getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/entity/guid';

/**
 * Sets the internal status of the entity with the given guid to DELETED. This counts as a soft delete in Atlas.
 * @param guid the guid of the entity
 */
export function deleteEntitySoft(guid: string) {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'deleteEntitySoft');

  const path = `${BASE_PATH}/${guid}`;

  return http.delete<EntityMutationResponse>(path);
}
