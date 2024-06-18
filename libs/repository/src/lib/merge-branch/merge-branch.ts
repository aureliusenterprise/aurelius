import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { BranchCommit } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface MergeBranchOptions {
  /** The name of the parser to use */
  readonly parserName?: 'archimate3';
  /** The comment provided by the user */
  readonly comment?: string;
}

/**
 * Makes an API call to move a branch to another branch. Has convenient default values for the optionals.
 */
export function mergeBranch(
  /** The full name of the project */
  projectName: string,
  /** The name of the source branch */
  fromBranch: string,
  /** The name of the target branch */
  toBranch: string,
  /** The username of the user making the merge */
  userid: string,
  /** Additional parameters for the merge branch operation */
  { parserName = 'archimate3', comment = '' }: MergeBranchOptions = {}
) {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/branch`;

  validateRequiredArguments(arguments, 'mergeBranch');

  let headers = new HttpHeaders();
  headers = headers.set('Content-Type', 'application/x-www-form-urlencoded');

  const formParams = createHttpParams({
    parserName,
    projectName,
    fromBranch,
    toBranch,
    userid,
    comment,
  });

  const requestOptions = {
    headers,
  };

  return http
    .authorize()
    .post<BranchCommit>(path, formParams.toString(), requestOptions);
}
