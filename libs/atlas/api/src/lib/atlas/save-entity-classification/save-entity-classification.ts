import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { Classification } from '../../types';
import { getHttpClient } from '../atlas-api.module';

/**
 * Adds the given `classifications` to the entity with the given `guid`.
 */
export function saveEntityClassification(
  /** The guid of the entity */
  guid: string,
  /** The classifications to add */
  classifications: Classification[]
): Observable<void> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'saveEntityClassification');

  const path = `atlas/v2/entity/guid/${guid}/classifications`;

  return http.post<void>(path, classifications);
}

/**
 * Changes the given `classifications` (e.g. whether they propagate) of the entity with the given `guid`. The entity
 * must already have them.
 */
export function updateEntityClassification(
  /** The guid of the entity */
  guid: string,
  /** The classifications to change */
  classifications: Classification[]
): Observable<void> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'updateEntityClassification');

  const path = `atlas/v2/entity/guid/${guid}/classifications`;

  return http.put<void>(path, classifications);
}
