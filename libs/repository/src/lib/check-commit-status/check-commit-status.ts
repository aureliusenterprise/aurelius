import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ModelQuery } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Makes an API call to check the status of an asynchronous backend operation
 */
export function checkCommitStatus(
  /** The ID of the operation assigned by the API */
  taskId: string,
  /** The full name of the project to which the operation is related */
  projectName: string
): Observable<ModelQuery> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/v2/query`;

  validateRequiredArguments(arguments, 'checkCommitStatus');

  let headers = new HttpHeaders();
  headers = headers.set('Accept', 'application/json');

  const queryParameters = createHttpParams({
    taskId,
    projectName,
  });

  const requestOptions = {
    headers: headers,
    params: queryParameters,
  };

  return http.authorize().get(path, requestOptions);
}
