import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { getHttpClient } from '../atlas-api.module';

export function getDashboard(forceUpdate = false): Observable<any> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getDashboard');

  const path = 'api/data_governance_dashboard';

  return http.cache(forceUpdate).get<any>(path);
}
