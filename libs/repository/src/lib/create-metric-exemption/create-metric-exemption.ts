import { validateRequiredArguments } from '@models4insight/utils';
import { repositoryApiBasePath } from '../constants';
import { MetricExemption } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Commits the given metric exemption to the database
 */
export function createMetricExemption(
  /** The metric exemption that should be committed */
  exemption: MetricExemption
) {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/exempt`;

  validateRequiredArguments(arguments, 'createMetricExemption');

  const params = createHttpParams(exemption);

  return http.authorize().post<MetricExemption>(path, params);
}
