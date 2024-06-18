import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AtlasTypesDef, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';

export function getTypeDefs(
  /** Optional parameters for the get type defs operation */
  { forceUpdate }: GetOptions = {}
): Observable<AtlasTypesDef> {
  const http = getHttpClient();
  validateRequiredArguments(arguments, 'getTypeDefs');

  const path = `atlas/v2/types/typedefs`;

  return http.cache(forceUpdate).get<AtlasTypesDef>(path);
}
