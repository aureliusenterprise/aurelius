import {
  b64toBlob,
  b64urlToB64,
  validateRequiredArguments,
} from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { modelviewBasePath } from '../constants';
import { createHttpParams, getHttpClient } from '../utils';

export function modelviewConvert(
  svg: string,
  width: number,
  height: number
): Observable<Blob> {
  const http = getHttpClient(),
    path = `${modelviewBasePath}/convert`;

  validateRequiredArguments(arguments, 'modelviewConvert');

  const formParams = createHttpParams({
    svg,
    width,
    height,
  });

  return http
    .authorize()
    .post(path, formParams, { responseType: 'text' })
    .pipe(map((response) => b64toBlob(b64urlToB64(response))));
}
