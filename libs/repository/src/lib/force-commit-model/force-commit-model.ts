import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ConflictResolutionTemplateEnum, ModelCommit } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Forcibly commit a model to the repository, resolving any conflicts
 */
export function forceCommitModel(
  /** Name of the parser used for interpreting the added file */
  parserName: string,
  /** Full name of the project to which the model should be committed */
  projectName: string,
  /** The name of the source branch */
  fromBranchName: string,
  /** ID of the module to which the model should be committed */
  module: string,
  /** The ID of the model that should be forcibly committed */
  fromModelId: string,
  /** The name of the target branch */
  toBranchName: string,
  /** The ID of the model that should be overwritten */
  toModelId: string,
  /** The username of the user that is triggering the commit */
  userid: string,
  /** The comment provided by the user */
  comment: string,
  /** The data format in which the model was provided */
  contentType: string,
  /** The original task ID as provided by the API */
  commitTaskId: string,
  /** The conflict resolution template to apply */
  template: ConflictResolutionTemplateEnum,
  /** A list of IDs representing which items to keep from the repository version of the model */
  addListLeft: string[] = [],
  /** A list of IDs representing which items to keep from the uploaded version of the model */
  addListRight: string[] = [],
  /** A list of IDs representing which items to discard from the repository version of the model */
  deleteListLeft: string[] = [],
  /** A list of IDs representing which items to discard from the uploaded version of the model */
  deleteListRight: string[] = []
): Observable<ModelCommit> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/v2/force`;

  let headers = new HttpHeaders();

  validateRequiredArguments(arguments, 'forceCommitModel');

  headers = headers.set('Content-Type', 'application/x-www-form-urlencoded');

  const formParams = createHttpParams({
    parserName,
    projectName,
    fromBranchName,
    module,
    fromModelId,
    toBranchName,
    toModelId,
    userid,
    comment,
    contentType,
    template,
    addListLeft,
    addListRight,
    deleteListLeft,
    deleteListRight,
    commitTaskId,
  });

  const requestOptions = {
    headers,
  };

  return http.authorize().post<ModelCommit>(path, formParams, requestOptions);
}
