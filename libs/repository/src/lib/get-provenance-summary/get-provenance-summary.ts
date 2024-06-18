import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, ModelProvenanceSummary } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface GetProvenanceSummaryOptions {
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
 * Makes an API request to retrieve a paged set of provenance summaries for the given project
 */
export function getProvenanceSummary(
  /** The full name of the project for which to retrieve the provenance */
  projectName: string,
  {
    batchSize,
    offset,
    queryString,
    branchName,
    latestOnly,
    from,
    until,
    forceUpdate,
  }: GetProvenanceSummaryOptions & GetOptions = {}
): Observable<ModelProvenanceSummary[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/provenance/hour`;

  validateRequiredArguments(arguments, 'getProvenanceSummary');

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
    .get<ModelProvenanceSummary[]>(path, requestOptions);
}
