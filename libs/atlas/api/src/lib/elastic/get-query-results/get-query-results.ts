import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AtlasSearchResult, GetOptions } from '../../types';
import { createHttpParams } from '../../utils';
import { getHttpClient } from '../elastic-api.module';

export interface GetQueryResultsOptions {
  /** Whether or not to exclude deleted entities from the search results */
  excludeDeletedEntities?: boolean;
  /** Limit the result set to only include the specified number of entries */
  limit?: number;
  /** Start offset of the result set (useful for pagination) */
  offset?: number;
}

const PATH = 'atlas/v2/search/basic';

/**
 * Retrieve data for the specified fulltext query
 */
export function getQueryResults(
  /** The fulltext query */
  query: string,
  /** Optional parameters for the get type defs operation */
  {
    excludeDeletedEntities = false,
    forceUpdate = false,
    limit = 0,
    offset = 0,
  }: GetOptions & GetQueryResultsOptions = {}
): Observable<AtlasSearchResult> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getQueryResults');

  const queryParameters = createHttpParams({
    excludeDeletedEntities,
    limit,
    offset,
    query,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<AtlasSearchResult>(PATH, requestOptions);
}
