import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, Project } from '../types';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to retrieve details about a specific project with the given projectId
 */
export function getProject(
  /** The ID of the project for which to retrieve the details */
  projectId: string,
  /** Optional parameters for the get project operation */
  { forceUpdate }: GetOptions = {}
): Observable<Project> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getProject');

  const path = `${repositoryApiBasePath}/project/${projectId}`;

  return http.authorize().cache(forceUpdate).get<Project>(path);
}
