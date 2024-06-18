import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, UserRole } from '../types';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to retrieve the role of the current user in the given project.
 * The identity of the user is derived from the bearer token
 */
export function getUserRole(
  /** The full name of the project for which to look up the role */
  projectName: string,
  /** Additional parameters for the get user role operation */
  { forceUpdate }: GetOptions = {}
): Observable<UserRole> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getUserRole');

  const path = `${repositoryApiBasePath}/auth/role/${projectName}`;

  return http.authorize().cache(forceUpdate).get<UserRole>(path);
}
