import { StoreSnapshot } from '@models4insight/redux';
import {
  circularReplacer,
  validateRequiredArguments,
} from '@models4insight/utils';
import { omit } from 'lodash';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { ErrorContext } from '../types';
import { getHttpClient } from '../utils';

/** Make an API call to report an error */
export function reportError(
  /** The name of the app from which the error is reported */
  appName: string,
  /** The version of the app from which the error is reported */
  appVersion: string,
  /** The error as thrown */
  error: Error,
  /** The username of the user reporting the error */
  userid: string,
  /** A snapshot of the current application state */
  state?: StoreSnapshot
): Observable<void> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/error`;

  validateRequiredArguments(arguments, 'reportError');

  const headers = {
    'Content-Type': 'application/json',
  };

  const body: ErrorContext = {
    app: appName,
    error: error,
    userid: userid,
    state: state,
    version: appVersion,
  };

  const requestOptions = { headers };

  // Sometimes the state cannot be serialized. In this case, omit the state from the payload.
  let payload: string;
  try {
    payload = JSON.stringify(body, circularReplacer());
  } catch {
    payload = JSON.stringify(omit(body, 'state'), circularReplacer());
  }

  return http.authorize().post<void>(path, payload, requestOptions);
}
