import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { ClassificationDef, GetOptions } from '../../types';
import { getHttpClient } from '../atlas-api.module';

const BASE_PATH = 'atlas/v2/types/classificationdef/name';

/**
 * Retrieves the classification type definition with the given `name` from the Atlas API
 */
export function getClassificationTypeByName(
  /** The name of the type */
  name: string,
  { forceUpdate = false }: GetOptions = {}
): Observable<ClassificationDef> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getClassificationTypeByName');

  const path = `${BASE_PATH}/${name}`;

  return http.cache(forceUpdate).get<ClassificationDef>(path);
}
