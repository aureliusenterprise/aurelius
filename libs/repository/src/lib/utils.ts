import { HttpClient, HttpParams } from '@angular/common/http';
import { HttpService } from '@models4insight/http';
import { Dictionary, isNaN, isNil } from 'lodash';
import { RepositoryModule } from './repository.module';

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

/**
 * Returns the `HttpService` as imported by the `RepositoryModule`. If the `RepositoryModule` has not been loaded, throws an error.
 */
export function getHttpClient(): HttpService {
  if (!RepositoryModule.injector) {
    throw new Error(
      'Tried running an API query while the RepositoryModule was not loaded. Please make sure the RepositoryModule is imported.'
    );
  }
  return RepositoryModule.injector.get(HttpClient) as HttpService;
}
