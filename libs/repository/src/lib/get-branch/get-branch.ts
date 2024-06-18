import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { Branch, GetOptions, Project } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Retrieves the `Branch` with the given `branchId` for the project with the given `projectId`
 */
export function getBranch(
  /** The id of the project for which to retrieve the branch */
  projectId: Project['id'],
  /** The id of the branch to retrieve */
  branchId: Branch['id'],
  /** Additional parameters for the getBranch operation */
  { forceUpdate }: GetOptions = {}
): Observable<Branch> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/branch`;

  validateRequiredArguments(arguments, 'getBranch');

  const queryParameters = createHttpParams({
    project_id: projectId,
    branch_id: branchId,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http.authorize().cache(forceUpdate).get<Branch>(path, requestOptions);
}
