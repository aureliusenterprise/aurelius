import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { getHttpClient } from '../utils';

export interface ClickstreamEvent {
  /** The name of the application */
  readonly app: string;
  /** The epoch time at which the event occurred */
  readonly timestamp: number;
  /** The path in the application that the user visited */
  readonly url: string;
  /** The username of the user */
  readonly userid: string;
}

/**
 * Saves the given clickstream event to the database
 */
export function logClickstreamEvent(
  /** The event that should be saved to the database */
  event: ClickstreamEvent
): Observable<void> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/log`;

  validateRequiredArguments(arguments, 'logClickstreamEvent');

  return http.authorize().post<void>(path, event);
}
