import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { getHttpClient } from '../atlas-api.module';

/**
 * Removes the classification with the given `classificationName` from the entity with the given `guid`.
 */
export function removeEntityClassification(
  /** The guid of the entity */
  guid: string,
  /** The name of the classification to remove */
  classificationName: string
): Observable<void> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'removeEntityClassification');

  const path = `atlas/v2/entity/guid/${guid}/classification/${classificationName}`;

  return http.delete<void>(path);
}
