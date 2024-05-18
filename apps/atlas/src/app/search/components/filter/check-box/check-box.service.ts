import { Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchFilters,
  AppSearchFilterSelection,
  AppSearchFilterValue,
  AppSearchFilterValues,
} from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Observable, Subject } from 'rxjs';
import { map, tap, withLatestFrom } from 'rxjs/operators';
import { SearchService } from '../../../services/search/search.service';

export interface CheckBoxStoreContext<
  T extends AppSearchDocument,
  K extends keyof T
> {
  readonly facet?: K;
  readonly value?: AppSearchFilterValue<T, K>;
  readonly count?: number;
}

function indexFiltersByKey<T extends AppSearchDocument>(
  filters: AppSearchFilters<T>
) {
  if (!filters?.all) {
    return {} as AppSearchFilterSelection<T>;
  }

  const entries = filters.all.flatMap((item) => Object.entries(item));

  return Object.fromEntries(entries) as AppSearchFilterSelection<T>;
}

@Injectable()
export class CheckBoxService<
  T extends AppSearchDocument,
  K extends keyof T
> extends BasicStore<CheckBoxStoreContext<T, K>> {
  readonly count$: Observable<number>;
  readonly facet$: Observable<K>;
  readonly value$: Observable<AppSearchFilterValue<T, K>>;

  readonly isSelected$: Observable<boolean>;

  private readonly updateFilterSelection$: Subject<boolean> =
    new Subject<boolean>();

  constructor(private readonly searchService: SearchService<T>) {
    super();

    this.updateFilterSelection$ = new Subject<boolean>();

    this.count$ = this.select('count');
    this.facet$ = this.select('facet');
    this.value$ = this.select('value');

    this.isSelected$ = combineLatest([
      this.searchService.select(['queryObject', 'filters'], {
        includeFalsy: true,
      }),
      this.facet$,
      this.value$,
    ]).pipe(
      map(([filters, facet, value]) => this.isSelected(filters, facet, value))
    );

    this.updateFilterSelection$
      .pipe(
        withLatestFrom(
          this.searchService.select(['queryObject', 'filters'], {
            includeFalsy: true,
          }),
          this.facet$,
          this.value$
        )
      )
      .pipe(untilDestroyed(this))
      .subscribe(([selectionState, filters, facet, value]) =>
        this.handleUpdateFilterSelection(selectionState, filters, facet, value)
      );
  }

  updateFilterSelection(selectionState: boolean) {
    this.updateFilterSelection$.next(selectionState);
  }

  private isSelected(
    filters: AppSearchFilters<T>,
    facet: K,
    value: AppSearchFilterValue<T, K>
  ) {
    if (!filters?.all) return false;

    const filtersByKey = indexFiltersByKey(filters);

    return (
      facet in filtersByKey && filtersByKey[facet as string].includes(value)
    );
  }

  private handleUpdateFilterSelection(
    selectionState: boolean,
    filters: AppSearchFilters<T>,
    facet: K,
    value: AppSearchFilterValue<T, K>
  ) {
    const filtersByKey = indexFiltersByKey(filters);

    let filterValues: AppSearchFilterValues<T, K> = filtersByKey[facet] ?? [];

    if (selectionState && !filterValues.includes(value)) {
      filterValues = [...filterValues, value];
    }

    if (!selectionState) {
      filterValues = filterValues.filter(
        (filterValue) => filterValue !== value
      );
    }

    filtersByKey[facet] = filterValues;

    if (filterValues.length === 0) {
      delete filtersByKey[facet];
    }

    this.searchService.filters = {
      all: Object.entries(filtersByKey).map(([key, filteredValues]) => ({
        [key]: filteredValues,
      })),
    };
  }
}
