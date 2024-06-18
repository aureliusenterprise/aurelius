import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AtlasEntityDef, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/types/entitydef/name';

/**
 * Retrieves the entity type definition with the given `name` from the Atlas API
 */
export function getTypeByName(
  /** The name of the type */
  name: string,
  { forceUpdate = false }: GetOptions = {}
): Observable<AtlasEntityDef> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getTypeByName');

  const path = `${BASE_PATH}/${name}`;

  return http.cache(forceUpdate).get<AtlasEntityDef>(path);
}
