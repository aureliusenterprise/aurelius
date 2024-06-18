import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import {
  AtlasEntityWithEXTInformation,
  EntityMutationResponse,
} from '../../types';
import { getHttpClient } from '../atlas-api.module';

const PATH = 'atlas/v2/entity';

/**
 * Saves the given `entity` to Atlas.
 */
export function saveEntity(
  /** The guid of the term */
  entity: AtlasEntityWithEXTInformation
): Observable<EntityMutationResponse> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'saveEntity');

  return http.post<EntityMutationResponse>(PATH, entity);
}
