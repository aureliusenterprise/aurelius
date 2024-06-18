import { HttpParams } from '@angular/common/http';
import { Dictionary, isNaN, isNil } from 'lodash';

/**
 * Creates a new `HttpParams` object based on the given parameters, filtering out any parameter of which the value is null or undefined
 */
export function createHttpParams(
  /** The set of key value pairs to include as parameters */
  params: Dictionary<any>
): HttpParams {
  let result: HttpParams = new HttpParams();
  Object.entries(params).forEach(([key, value]) => {
    if (!isNil(value) && !isNaN(value)) {
      result = result.set(key, value);
    }
  });
  return result;
}
