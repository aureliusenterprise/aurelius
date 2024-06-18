import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { Branch } from '../types';
import { getHttpClient } from '../utils';

/**
 * Creates or updates the given `Branch` in the repository.
 * Whether a `Branch` is updated or created depends on whether or not the `branch_id` property is set.
 */
export function updateBranch(
  /** The branch which to create or update */
  branch: Branch
) {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/project/branch`;

  validateRequiredArguments(arguments, 'updateBranch');

  return http.authorize().post<Branch>(path, branch);
}
