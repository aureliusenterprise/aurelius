import { GetOptions, UserInfo } from '../types';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to retrieve the user info for the current user.
 * The API interprets the Bearer token in the request header to determine which user info to return.
 */
export function getUserInfo({
  forceUpdate,
}: GetOptions = {}): Observable<UserInfo> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/user`;

  return http.authorize().cache(forceUpdate).get<UserInfo>(path);
}
