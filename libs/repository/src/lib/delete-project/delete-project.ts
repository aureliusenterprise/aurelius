import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to delete a specific project and all associated models
 */
export function deleteProject(
  /** The ID of the project to delete */
  projectId: string
) {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'deleteProject');

  const path = `${repositoryApiBasePath}/project/${projectId}`;

  return http.authorize().delete(path);
}
