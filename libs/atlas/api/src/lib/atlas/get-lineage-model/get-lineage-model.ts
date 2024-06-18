import { validateRequiredArguments } from '@models4insight/utils';
import { GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';
import { createHttpParams } from '../../utils';

export type LineageDirection = 'INPUT' | 'OUTPUT' | 'BOTH';

export interface GetLineageModelOptions {
  /** Specifies the maximum number of hops to traverse the lineage graph */
  readonly depth?: number;
  /** Specifies whether to retrieve input lineage, output lineage or both */
  readonly direction?: LineageDirection;
}

const PATH = 'lineage_model';

/**
 * Fetch the lineage of an entity given its `guid`.
 *
 *  Options:
 *  * You can use `depth` to specify the maximum number of hops to traverse the lineage graph. Default is 3.
 *  * You can use `direction` to specify whether to retrieve input lineage, output lineage or both. Default is both.
 *
 * @param guid The unique atlas id of the enitity for which to retrieve the lineage
 */
export function getLineageModel(
  guid: string,
  {
    depth = 3,
    direction = 'BOTH',
    forceUpdate,
  }: GetOptions & GetLineageModelOptions = {}
) {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getEntityById');

  const queryParameters = createHttpParams({
    guid,
    depth,
    direction,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http.cache(forceUpdate).get<any>(PATH, requestOptions);
}
