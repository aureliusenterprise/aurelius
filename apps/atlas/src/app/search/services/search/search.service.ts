import { Inject, Injectable, InjectionToken, Optional } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchFacets,
  AppSearchFields,
  AppSearchFilters,
  AppSearchQuery,
  AppSearchSort,
} from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { Observable } from 'rxjs';

export const $DEFAULT_QUERY = new InjectionToken<
  AppSearchQuery<AppSearchDocument>
>('DEFAULT_QUERY');

export interface SearchState<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> {
  readonly queryObject?: AppSearchQuery<T, P>;
}

@Injectable()
export class SearchService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> extends BasicStore<SearchState<T, P>> {
  readonly queryObject$: Observable<AppSearchQuery<T, P>>;

  constructor(
    @Optional()
    @Inject($DEFAULT_QUERY)
    defaultQuery?: AppSearchQuery<T, P>
  ) {
    super({
      defaultState: { queryObject: defaultQuery },
    });
    this.queryObject$ = this.select('queryObject');
  }

  set query(query: string) {
    this.update({
      description: 'New query available',
      path: ['queryObject', 'query'],
      payload: query ?? '',
    });
  }

  set queryObject(queryObject: AppSearchQuery<T, P>) {
    this.update({
      description: 'New query object available',
      payload: { queryObject },
    });
  }

  set facets(facets: AppSearchFacets<T>) {
    this.update({
      description: 'New facets available',
      path: ['queryObject', 'facets'],
      payload: facets,
    });
  }

  set filters(filters: AppSearchFilters<T>) {
    this.update({
      description: 'New filters available',
      path: ['queryObject', 'filters'],
      payload: filters,
    });
  }

  set resultFields(resultFields: AppSearchFields<P>) {
    this.update({
      description: 'New result fields available',
      path: ['queryObject', 'result_fields'],
      payload: resultFields,
    });
  }

  set sort(sort: AppSearchSort<T>) {
    this.update({
      description: 'New sort available',
      path: ['queryObject', 'sort'],
      payload: sort,
    });
  }
}
