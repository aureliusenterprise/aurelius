import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, Project, UserGroup } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Retrieves all `UserGroup` for the project with the given `projectId`
 */
export function getUserGroups(
  /** The id of the project for which to retrieve the user groups */
  projectId: Project['id'],
  /** Additional parameters for the getUserGroups operation */
  { forceUpdate }: GetOptions = {}
): Observable<UserGroup[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/group`;

  validateRequiredArguments(arguments, 'getUserGroups');

  const queryParameters = createHttpParams({
    project_id: projectId,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<UserGroup[]>(path, requestOptions);
}
