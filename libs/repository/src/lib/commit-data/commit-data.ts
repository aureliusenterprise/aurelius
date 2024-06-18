import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { getHttpClient } from '../utils';

/**
 * Commit a dataset associated with a model to the repository
 */
export function commitData(
  /** The full name of the project to which the data should be committed */
  projectName: string,
  /** The name of the branch to which the data should be committed */
  branchName: string,
  /** The actual data to be committed. Defaults to an empty array */
  content: any[] = [],
  /** The id of the model to which the data should be committed. Defaults to 'TRUNK' */
  model_id: string = 'TRUNK'
): Observable<string> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/data`;

  validateRequiredArguments(arguments, 'commitData');

  const body = {
    project: projectName,
    branch: branchName,
    model_id: model_id,
    content: content,
  };

  return http
    .authorize()
    .post<string>(path, body, { responseType: 'text' as 'json' });
}
