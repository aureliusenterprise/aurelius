import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AtlasEntityWithEXTInformation, GetOptions } from '../../types';
import { getHttpCache, getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/entity/guid';

/** Clears the HTTP cache for the entity with the given `guid` */
export function clearEntityByIdCache(
  //** The guid of the entity */
  guid: string
) {
  const cache = getHttpCache();
  cache.clearCache(`${BASE_PATH}/${guid}`);
}

/**
 * Retrieves the entity with the given `guid` from the Atlas API
 */
export function getEntityById(
  /** The guid of the entity */
  guid: string,
  { forceUpdate = false }: GetOptions = {}
): Observable<AtlasEntityWithEXTInformation> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getEntityById');

  const path = `${BASE_PATH}/${guid}`;

  return http.cache(forceUpdate).get<AtlasEntityWithEXTInformation>(path);
}
