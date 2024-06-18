import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ModelCommit } from '../types';
import { getHttpClient } from '../utils';

export interface CommitJsonOptions {
  /** The parser that should be used to interpret the file */
  readonly parserName?: 'archimate3';
  /** The ID of the module to which the model should be committed */
  readonly module?: string;
  /** The comment provided by the user */
  readonly comment?: string;
}

/**
 * Commits a model to the repository as a JSON string
 */
export function commitJsonModel(
  /** The full name of the project to which the model should be committed */
  projectName: string,
  /** The name of the branch to which the model should be committed */
  toBranchName: string,
  /** The JSON string representing the model */
  json: string,
  /** The username of the user committing the model */
  userid: string,
  /** Optional parameters for the commit operation */
  {
    parserName = 'archimate3',
    module = '',
    comment = '',
  }: CommitJsonOptions = {}
): Observable<ModelCommit> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/v2/commitJson`;

  validateRequiredArguments(arguments, 'commitJsonModel');

  const body = {
    projectName: projectName,
    branch: toBranchName,
    userid: userid,
    type: parserName,
    comment: comment,
    raw: json,
  };

  return http.authorize().post<ModelCommit>(path, body);
}
