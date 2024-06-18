import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { modelCompareBasePath } from '../constants';
import { GetOptions, ModelCompareResult } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface CompareModelsOptions {
  /** Specify the version of the base model to compare a specific version. If omitted, compare the latest version of the base branch. */
  baseVersion?: number;
  /** Specify the version of the other model to compare a specific version. If omitted, compare the latest version of the other branch. */
  otherVersion?: number;
}

export function compareModels(
  project: string,
  baseBranchName: string,
  otherBranchName: string,
  {
    baseVersion,
    forceUpdate,
    otherVersion,
  }: CompareModelsOptions & GetOptions = {}
): Observable<ModelCompareResult> {
  const http = getHttpClient(),
    path = modelCompareBasePath;

  validateRequiredArguments(arguments, 'compareModels');

  const queryParameters = createHttpParams({
    project,
    baseBranch: baseBranchName,
    baseVersion,
    otherBranch: otherBranchName,
    otherVersion,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<ModelCompareResult>(path, requestOptions);
}
