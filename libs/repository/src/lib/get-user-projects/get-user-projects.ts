import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, Project } from '../types';
import { getHttpClient } from '../utils';

/**
 * Retrieve a list of projects the given user owns or has permission to access
 */
export function getUserProjects(
  /** The username of the user for whom to retrieve the projects */
  userId: string,
  /** Optional parameters for the get user projects operation */
  { forceUpdate }: GetOptions = {}
): Observable<Project[]> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getUserProjects');

  const path = `${repositoryApiBasePath}/project/user/${userId}`;

  return http.authorize().cache(forceUpdate).get<Project[]>(path);
}
