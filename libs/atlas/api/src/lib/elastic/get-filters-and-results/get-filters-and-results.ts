import { validateRequiredArguments } from '@models4insight/utils';
import { Observable } from 'rxjs';
import {
  ElasticSearchResults,
  Facets,
  FilterValuesByFieldName,
  GetOptions,
  SortingDirectionByFieldName,
} from '../../types';
import { getHttpClient } from '../elastic-api.module';

export function getFiltersAndResults(
  query: string,
  facets: Facets,
  result_fields,
  page: {
    size: number;
    current: number;
  },
  filters: FilterValuesByFieldName,
  sort?: SortingDirectionByFieldName,
  { forceUpdate }: GetOptions = {}
): Observable<ElasticSearchResults> {
  const http = getHttpClient();

  validateRequiredArguments(arguments, 'getFiltersAndResults');

  const path = 'elastic';

  return http.cache(forceUpdate).post<ElasticSearchResults>(path, {
    query,
    facets,
    filters,
    page,
    result_fields,
    sort,
  });
}
