import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { GetOptions, MetricExemption } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

export interface GetMetricExemptionOptions {
  /** You can specify the branch id if you only want the exemptions for a particular branch */
  branchId?: string;
  /** You can specify a metric name if you want to limit the exemptions to the metric with that name */
  metricName?: string;
  /** You can specify the version timestamp if you only want the exemptions for a particular version */
  version?: number;
}

/**
 * Retrieves all `MetricExemption` for the project with the given `projectId`.
 * You can optionally supply a branch id, metric name and version timestamp to limit the results.
 */
export function getMetricExemption(
  /** The id of the project for which to retrieve the exemptions */
  projectId: string,
  /** Additional options for the getMetricExemption operation */
  {
    branchId,
    forceUpdate,
    metricName,
    version,
  }: GetOptions & GetMetricExemptionOptions = {}
): Observable<MetricExemption[]> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/exempt`;

  validateRequiredArguments(arguments, 'getMetricExemption');

  const params = createHttpParams({
    project_id: projectId,
    branch: branchId,
    metric: metricName,
    version,
  });

  return http
    .cache(forceUpdate)
    .authorize()
    .get<MetricExemption[]>(path, { params });
}
