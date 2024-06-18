import { Action, ActionType } from '@models4insight/redux';
import { validateRequiredArguments } from '@models4insight/utils';
import { now } from 'lodash';
import { Observable } from 'rxjs';
import { repositoryLogBasePath } from '../constants';
import { getHttpClient } from '../utils';

/**
 * Commit a history of redux events to the repository
 */
export function commitEventLog(
  sessionId: string,
  event: Action<any>
): Observable<void> {
  const http = getHttpClient(),
    path = `${repositoryLogBasePath}/event`;

  validateRequiredArguments(arguments, 'commitEventLog');

  let eventPath: (string | number)[];
  if (event.type === ActionType.UPDATE || event.type === ActionType.DELETE) {
    eventPath = event.path;
  }

  const body = {
    sessionId,
    event: {
      description: event.description,
      path: eventPath,
      timestamp: now(),
      type: event.type,
    },
  };

  return http.post<void>(path, body);
}
