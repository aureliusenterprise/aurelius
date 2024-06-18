import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, Project, UserGroup } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Retrieves the `UserGroup` with the given `userGroupId` for the project with the given `projectId`
 */
export function getUserGroup(
  /** The id of the project for which to retrieve the user group */
  projectId: Project['id'],
  /** The id of the user group to retrieve */
  userGroupId: UserGroup['id'],
  /** Additional parameters for the getUserGroup operation */
  { forceUpdate }: GetOptions = {}
): Observable<UserGroup> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/group`;

  validateRequiredArguments(arguments, 'getUserGroup');

  const queryParameters = createHttpParams({
    project_id: projectId,
    group_id: userGroupId,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<UserGroup>(path, requestOptions);
}
