import { Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchResultsFacet,
  AppSearchResultsFacetData,
  AppSearchResultsFacets,
} from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AppSearchResultsService } from '../app-search-results/app-search-results.service';

export type SearchFilters<T extends AppSearchDocument> = {
  [K in keyof T]?: AppSearchResultsFacetData<T, T[K]>[];
};

export interface SearchFilterContext<T extends AppSearchDocument> {
  readonly filters?: SearchFilters<T>;
}

@Injectable()
export class FilterService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> extends BasicStore<SearchFilterContext<T>> {
  filters$: Observable<SearchFilters<T>>;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<T, P>
  ) {
    super();

    this.filters$ = this.select('filters');

    this.searchResultsService.facets$
      .pipe(untilDestroyed(this))
      .subscribe((facets) => this.updateFilters(facets));
  }

  set filters(filters: SearchFilters<T>) {
    this.update({
      description: 'New filters available',
      payload: { filters },
    });
  }

  private updateFilters(facets: AppSearchResultsFacets<T>) {
    function formatEntry<K extends keyof T>(
      key: K,
      facet: AppSearchResultsFacet<T, T[K]>
    ) {
      return [key, facet.data] as const;
    }

    const entries = Object.entries(facets) as [
      keyof T,
      AppSearchResultsFacet<T, T[keyof T]>[]
    ][];

    const facetData = entries
      .map(([key, [facet]]) => formatEntry(key, facet))
      .filter(([_, facet]) => facet.length > 0);

    this.filters = Object.fromEntries(facetData) as SearchFilters<T>;
  }
}
