import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ModelQuery } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Retrieve the details for a conflict or a set of conflicts
 */
export function getModelConflict(
  /** The ID of the operation that resulted in the conflicts */
  taskId: string,
  /** The full name of the project to which the conflicts belong */
  projectName: string,
  /** The inclusive index at which to start the page */
  index: number,
  /** The length of the page */
  limit: number
): Observable<ModelQuery> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/v2/conflict`;

  validateRequiredArguments(arguments, 'getModelConflict');

  let headers = new HttpHeaders();
  headers = headers.set('Accept', 'application/json');

  const queryParameters = createHttpParams({
    taskId,
    projectName,
    index,
    limit,
  });

  const requestOptions = {
    headers,
    params: queryParameters,
  };

  return http.authorize().cache().get<ModelQuery>(path, requestOptions);
}
