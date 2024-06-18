import { Inject, Injectable, InjectionToken } from '@angular/core';
import { Observable } from 'rxjs';
import { Facet, Field, Meta } from '../types';
import { AppSearchClient } from './app-search-client.service';

export const $APP_SEARCH_PATH = new InjectionToken<string>('APP_SEARCH_PATH');

export interface AppSearchDocument {
  readonly guid?: string;
  readonly id?: string;
  readonly name?: string;
}

export type AppSearchFacets<T extends AppSearchDocument> = {
  readonly [FieldName in keyof T]?: Facet;
};

export type AppSearchFilterValue<
  T extends AppSearchDocument,
  K extends keyof T
> = T[K] extends Array<infer V> ? V : T[K];

export type AppSearchFilterValues<
  T extends AppSearchDocument,
  K extends keyof T
> = AppSearchFilterValue<T, K>[];

export type AppSearchFilterSelection<T extends AppSearchDocument> = {
  [K in keyof T]?: AppSearchFilterValues<T, K>;
};

export type AppSearchFilters<T extends AppSearchDocument> = {
  [A in 'all' | 'any' | 'none']?: (
    | AppSearchFilters<T>
    | AppSearchFilterSelection<T>
  )[];
};

export type AppSearchFields<T extends AppSearchDocument> = {
  readonly [FieldName in keyof T]: Field;
};

export interface AppSearchPage {
  readonly current: number;
  readonly size: number;
}

export type AppSearchSortDirection = 'asc' | 'desc';

export type AppSearchSortKey<T extends AppSearchDocument> = keyof T | '_score';

export type AppSearchSort<T extends AppSearchDocument> = {
  readonly [fieldName in AppSearchSortKey<T>]?: AppSearchSortDirection;
};

export interface AppSearchQuery<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> {
  readonly facets: AppSearchFacets<T>;
  readonly page: AppSearchPage;
  readonly query: string;
  readonly filters?: AppSearchFilters<T>;
  readonly result_fields?: AppSearchFields<P>;
  readonly sort?: AppSearchSort<T>;
}

export interface AppSearchResultObject<T> {
  readonly raw: T;
  readonly snippet?: string;
}

export type AppSearchResult<T extends AppSearchDocument> = {
  readonly [FieldName in keyof T]: AppSearchResultObject<T[FieldName]>;
};

export interface AppSearchResultsFacetData<
  T extends AppSearchDocument,
  V extends T[keyof T]
> {
  readonly value: V;
  readonly count: number;
}

export interface AppSearchResultsFacet<
  T extends AppSearchDocument,
  V extends T[keyof T]
> {
  readonly type: string;
  readonly data: AppSearchResultsFacetData<T, V>[];
}

export type AppSearchResultsFacets<T extends AppSearchDocument> = {
  [F in keyof T]?: AppSearchResultsFacet<T, T[F]>[];
};

export interface AppSearchResults<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> {
  readonly meta?: Meta;
  readonly results?: AppSearchResult<P>[];
  readonly facets?: AppSearchResultsFacets<T>;
}

@Injectable()
export class AppSearchService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> {
  constructor(
    private readonly http: AppSearchClient,
    @Inject($APP_SEARCH_PATH) private readonly PATH: string
  ) {}

  search(
    queryObject: AppSearchQuery<T, P>
  ): Observable<AppSearchResults<T, P>> {
    return this.http.post<AppSearchResults<T, P>>(this.PATH, queryObject);
  }
}
