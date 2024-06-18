import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface RetrieveModelOptions {
  observe?: any;
  responseType?: any;
  /** The timestamp at which the model that should be retrieved was originally committed */
  version?: number;
}

/**
 * Retrieve a version of a model from the given project and branch in a particular format. If no version is given, retrieves the latest version.
 */
export function getModel(
  /** Name of the parser used for interpreting the added file */
  parserName: string,
  /** The full name of the project from which to retrieve the model */
  projectName: string,
  /** The name of the branch from which to retrieve the model */
  branchName: string,
  /** The ID of the module which to retrieve */
  module: string,
  /** The ID of the model which to retrieve */
  modelId: string,
  /** The username of the user retrieving the model */
  userid: string,
  /** The format in which to retrieve the model */
  contentType: string,
  /** Additional parameters for the retrieve operation */
  {
    forceUpdate,
    observe,
    responseType,
    version,
  }: RetrieveModelOptions & GetOptions = {}
): Observable<any> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/retrieve`;

  validateRequiredArguments(arguments, 'getModel');

  let headers = new HttpHeaders();
  headers = headers.set('Content-Type', 'application/x-www-form-urlencoded');

  const queryParameters = createHttpParams({
    parserName,
    projectName,
    branchName,
    module,
    modelId,
    userid,
    version,
    contentType,
  });

  const requestOptions = {
    headers,
    params: queryParameters,
    observe,
    responseType: responseType || (contentType === 'json' ? 'json' : 'text'),
  };

  return http.authorize().cache(forceUpdate).get(path, requestOptions);
}
