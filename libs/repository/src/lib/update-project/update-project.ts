import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { Project } from '../types';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to update an existing project; project names are immutable
 */
export function updateProject(
  /** The ID of the project to update */
  projectId: string,
  /** The updated project data object */
  project: Project
): Observable<Project> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'updateProject');

  const path = `${repositoryApiBasePath}/project/${projectId}`;

  return http.authorize().post(path, project);
}
