import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { BranchSummary, GetOptions } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface GetBranchesSummaryOptions {
  /** The number of summaries to retrieve */
  readonly batchSize?: number;
  /** The inclusive index of the summary to start the page at */
  readonly offset?: number;
  /** Select only the branches whose name includes this string */
  readonly queryString?: string;
  /** Select only the branches whose name matches this string */
  readonly branchName?: string;
  /** Select only the most recent updates for each branch */
  readonly latestOnly?: boolean;
  /** Select only the branch updates after this timestamp */
  readonly from?: number;
  /** Select only the branch updates before this timestamp */
  readonly until?: number;
}

/**
 * Makes an API call to retrieve a paged summary of all branches in the project
 */
export function getBranchesSummary(
  /** The full name of the project for which to retrieve the branch summary */
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
  }: GetBranchesSummaryOptions & GetOptions = {}
): Observable<BranchSummary[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/branch`;

  validateRequiredArguments(arguments, 'getBranchesSummary');

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
    .get<BranchSummary[]>(path, requestOptions);
}
