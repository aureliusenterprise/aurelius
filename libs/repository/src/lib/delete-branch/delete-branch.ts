import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Deletes the branch with the given `projectId` and `branchId` from the repository.
 * Branches are not actually deleted, but have their `enabled` property set to `false` in the database.
 */
export function deleteBranch(
  /** The id of the project for which a branch should be deleted */
  projectId: string,
  /** The id of the branch which should be deleted */
  branchId: string
): Observable<string> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/branch`;

  validateRequiredArguments(arguments, 'deleteBranch');

  const requestParameters = createHttpParams({
    project_id: projectId,
    branch_id: branchId,
  });

  const requestOptions = {
    params: requestParameters,
    responseType: 'text' as 'text',
  };

  return http.authorize().delete(path, requestOptions);
}
