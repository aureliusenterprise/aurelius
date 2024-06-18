import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { userSearchBasePath } from '../constants';
import { GetOptions, UserSearch } from '../types';
import { createHttpParams, getHttpClient } from '../utils';

/**
 * Get the user details matching the search string
 */
export function userSearch(
  /** String to match the first name, last name, username or email address of any users */
  search: string,
  { forceUpdate }: GetOptions = {}
): Observable<UserSearch[]> {
  const http = getHttpClient(),
    path = userSearchBasePath;

  validateRequiredArguments(arguments, 'userSearch');

  let headers = new HttpHeaders();
  headers = headers.set('Content-Type', 'application/json');

  const queryParameters = createHttpParams({ search });

  const requestOptions = {
    headers,
    params: queryParameters,
  };

  return http
    .authorize()
    .cache(forceUpdate)
    .get<UserSearch[]>(path, requestOptions);
}
