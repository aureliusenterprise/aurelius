import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ModelCommit, ModelCommitContentTypeEnum } from '../types';
import { getHttpClient } from '../utils';

export interface CommitModelOptions {
  /** The comment provided by the user */
  readonly comment?: string;
  /** The content type of the file */
  readonly contentType?: ModelCommitContentTypeEnum;
  /** Whether or not to create new ids for new concepts, or use the ids already present */
  readonly keepOriginalIds?: boolean;
  /** The parser that should be used to interpret the file */
  readonly parserName?: 'archimate3';
  /** The ID of the module to which the model should be committed */
  readonly module?: string;
  /** The ID of the model that should be overwritten */
  readonly modelId?: string;
}

/**
 * Commits a model to the repository as a File
 */
export function commitModel(
  /** The full name of the project to which the model should be committed */
  projectName: string,
  /** The name of the branch to which the model should be committed */
  toBranchName: string,
  /** The file containing the model */
  file: File,
  /** The username of the user committing the model */
  userid: string,
  /** Optional parameters for the commit operation */
  {
    keepOriginalIds = false,
    parserName = 'archimate3',
    module = '',
    modelId = 'TRUNK',
    comment = '',
    contentType = ModelCommitContentTypeEnum.ARCHIMATE,
  }: CommitModelOptions = {}
): Observable<ModelCommit> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/model/v2/commit`;

  validateRequiredArguments(arguments, 'commitModel');

  const formParams = new FormData();

  formParams.append('parserName', parserName);
  formParams.append('projectName', projectName);
  formParams.append('toBranchName', toBranchName);
  formParams.append('module', module);
  formParams.append('modelId', modelId);
  formParams.append('userid', userid);
  formParams.append('comment', comment);
  formParams.append('contentType', contentType);
  formParams.append('keepOriginalIds', Boolean(keepOriginalIds).toString());
  formParams.append('file', file, file.name);

  return http.authorize().post<ModelCommit>(path, formParams);
}
