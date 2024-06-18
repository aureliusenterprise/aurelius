import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { GetOptions, TermDetails } from '../../types';
import { createHttpParams } from '../../utils';
import { getHttpClient } from '../atlas-api.module';

export interface GetTermsDefinitionByIdOptions {
  /** Whether or not to ignore relationships from the results, defaults to false */
  ignoreRelationships?: boolean;
  /** Wether or not to consider outside information, defaults to false */
  minExtInfo?: boolean;
}
const BASE_PATH = 'atlas/v2/glossary/term';

export function getTermsDefinitionById(
  /** The guid of the term entity */
  guid: string,
  {
    ignoreRelationships = false,
    minExtInfo = false,
    forceUpdate = false,
  }: GetOptions & GetTermsDefinitionByIdOptions = {}
): Observable<TermDetails> {
  const http = getHttpClient();
  validateRequiredArguments(arguments, 'getTermsDefinitionById');

  const path = `${BASE_PATH}/${guid}`;

  const queryParameters = createHttpParams({
    ignoreRelationships,
    minExtInfo,
  });

  const requestOptions = {
    params: queryParameters,
  };

  return http.cache(forceUpdate).get<TermDetails>(path, requestOptions);
}
