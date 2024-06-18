import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { PermissionLevel, Project } from '../types';
import { getHttpClient } from '../utils';

/** Adds default permissions, committer information and a default update message to the given project */
export function initializeProject(
  /** The data object representing the project */
  project: Project,
  /** The username of the user to whom the project belongs */
  username: string,
  /** The email address of the user to whom the project belongs */
  email: string
): Project {
  return {
    ...project,
    permissions: {
      [username]: PermissionLevel.OWNER,
    },
    last_update_message: 'project creation',
    committer: {
      username,
      email,
    },
  };
}

/** Create a project with some default values */
export function createProject(
  /** The data object representing the project */
  project: Project,
  /** The username of the user to whom the project belongs */
  username: string,
  /** The email address of the user to whom the project belongs */
  email: string
) {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project`;

  validateRequiredArguments(arguments, 'createProject');

  const initializedProject: Project = initializeProject(
    project,
    username,
    email
  );

  return http.authorize().post<Project>(path, initializedProject);
}
