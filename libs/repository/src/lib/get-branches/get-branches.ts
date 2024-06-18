import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { Branch, GetOptions, Project } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Retrieves all `Branch` for the project with the given `projectId`
 */
export function getBranches(
  /** The id of the project for which to retrieve the branches */
  projectId: Project['id'],
  /** Additional parameters for the getBranches operation */
  { forceUpdate }: GetOptions = {}
): Observable<Branch[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/branch`;

  validateRequiredArguments(arguments, 'getBranches');

  const queryParameters = createHttpParams({
    project_id: projectId,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<Branch[]>(path, requestOptions);
}
