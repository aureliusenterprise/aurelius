import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Deletes the `UserGroup` with the given `projectId` and `userGroupId` from the repository.
 */
export function deleteUserGroup(
  projectId: string,
  userGroupId: string
): Observable<string> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/group`;

  validateRequiredArguments(arguments, 'deleteUserGroup');

  const requestParameters = createHttpParams({
    project_id: projectId,
    group_id: userGroupId,
  });

  const requestOptions = {
    params: requestParameters,
    responseType: 'text' as 'text',
  };

  return http.authorize().delete(path, requestOptions);
}
