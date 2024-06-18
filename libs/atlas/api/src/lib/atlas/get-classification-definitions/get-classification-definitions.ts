import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { ClassificationResponse, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';
import { createHttpParams } from '../../utils';

export interface GetClassificationsDefinitionsOptions {
  /** Whether or not to ignore relationships from the results, defaults to false */
  ignoreRelationships?: boolean;
  /** Wether or not to consider outside information, defaults to false */
  minExtInfo?: boolean;
}

export function getClassificationsDefinitions({
  ignoreRelationships = false,
  minExtInfo = false,
  forceUpdate = false,
}: GetOptions &
  GetClassificationsDefinitionsOptions = {}): Observable<ClassificationResponse> {
  const http = getHttpClient();
  validateRequiredArguments(arguments, 'getClassificationsDefinitions');

  const path = 'atlas/v2/types/typedefs?type=classification';

  const queryParameters = createHttpParams({
    ignoreRelationships,
    minExtInfo,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http.cache(forceUpdate).get<any>(path, requestOptions);
}
