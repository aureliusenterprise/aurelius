import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { UserGroup } from '../types';
import { getHttpClient } from '../utils';

/**
 * Creates or updates the given `UserGroup` in the repository.
 * Whether a `UserGroup` is updated or created depends on whether or not the `group_id` property is set.
 */
export function updateUserGroup(
  /** The user group which to create or update */
  userGroup: UserGroup
): Observable<UserGroup> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/group`;

  validateRequiredArguments(arguments, 'updateUserGroup');

  return http.authorize().post<UserGroup>(path, userGroup);
}
