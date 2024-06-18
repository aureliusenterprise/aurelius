import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, ModelProvenance } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface GetProvenanceOptions {
  /** The number of provenance items to retrieve */
  readonly batchSize?: number;
  /** The inclusive index at which to start the page */
  readonly offset?: number;
  /** The provenance item should include this string */
  readonly queryString?: string;
  /** The branch for the provenance item should match this name */
  readonly branchName?: string;
  /** Only include the latest provenance items for each branch */
  readonly latestOnly?: boolean;
  /** Only include provenance items from after this timestamp */
  readonly from?: number;
  /** Only include provenance items from before this timestamp */
  readonly until?: number;
}

/**
 * Makes an API request for a paged set of provenance items for the given project
 */
export function getProvenance(
  /** The full name of the project for which to retrieve the provenance */
  projectName: string,
  /** Additional query parameters */
  {
    batchSize,
    offset,
    queryString,
    branchName,
    latestOnly,
    from,
    until,
    forceUpdate,
  }: GetProvenanceOptions & GetOptions = {}
): Observable<ModelProvenance[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/provenance`;

  validateRequiredArguments(arguments, 'getProvenance');

  const queryParameters = createHttpParams({
    projectName,
    pageLength: batchSize,
    pageOffset: offset,
    query: queryString,
    branchName,
    latestOnly,
    startDate: from,
    endDate: until,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<ModelProvenance[]>(path, requestOptions);
}
