import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { getHttpClient } from '../utils';

/**
 * Delete an exemption from the database which:
 * - Belongs to the metric with the given name and project with the given id, and
 * - Has the given exemption id
 */
export function deleteMetricExemption(
  /** The id of the project to which the exemption belongs */
  projectId: string,
  /** The id of the exemption */
  exemptionId: string
) {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/exempt/${projectId}/${exemptionId}`;

  validateRequiredArguments(arguments, 'deleteMetricExemption');

  return http.authorize().delete(path);
}
