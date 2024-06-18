import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AtlasSearchResult, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';

export function getDomains(
  /** Optional parameters for the get domains operation */
  { forceUpdate }: GetOptions = {}
): Observable<AtlasSearchResult> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getDomains');

  const path = `atlas/v2/search/basic/?typeName=m4i_data_domain`;

  return http.cache(forceUpdate).get<AtlasSearchResult>(path);
}
