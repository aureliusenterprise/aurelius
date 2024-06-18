import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { GetOptions, TermDetails } from '../../types';
import { getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/glossary/term';

/**
 * Retrieves the term with the given `guid` from the Atlas API
 */
export function getTermById(
  /** The guid of the term */
  guid: string,
  { forceUpdate = false }: GetOptions = {}
): Observable<TermDetails> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getTermById');

  const path = `${BASE_PATH}/${guid}`;

  return http.cache(forceUpdate).get<TermDetails>(path);
}
