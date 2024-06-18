import { HttpHeaders } from '@angular/common/http';
import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { repositoryApiBasePath } from '../constants';
import { UserInfo } from '../types';
import { getHttpClient } from '../utils';

/**
 * Makes an API request to update the user info for the current user.
 * The API interprets the Bearer token in the request header to determine which user info to update.
 */
export function updateUserInfo(
  /** The new user info */
  userinfo: UserInfo
): Observable<UserInfo> {
  const http = getHttpClient(),
    path = `${repositoryApiBasePath}/user/update`;

  validateRequiredArguments(arguments, 'updateUserInfo');

  let headers = new HttpHeaders();
  headers = headers.set('Content-Type', 'application/json');

  const requestOptions = {
    headers,
  };

  return http.authorize().post<UserInfo>(path, userinfo, requestOptions);
}
