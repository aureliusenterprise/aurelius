import { Injectable, OnDestroy } from '@angular/core';
import { Sort } from '@angular/material/sort';
import { BasicStore, StoreService } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest, Subject } from 'rxjs';
import { withLatestFrom } from 'rxjs/operators';

export interface SortableTableShellStoreContext<
  T extends Dictionary<any> = Dictionary<any>
> {
  readonly currentPage?: number;
  readonly data?: T[];
  readonly selectedRow?: T;
  readonly sort?: Sort;
  readonly sortedData?: T[];
}

export const sortableTableShellServiceDefaultState: SortableTableShellStoreContext =
  {
    currentPage: 0,
    data: [],
    selectedRow: {},
    sort: {} as Sort,
    sortedData: [],
  };

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable()
export class SortableTableShellService<
    T extends Dictionary<any> = Dictionary<any>
  >
  extends BasicStore<SortableTableShellStoreContext<T>>
  implements OnDestroy
{
  private rowSelected$: Subject<T> = new Subject<T>();

  constructor(storeService: StoreService) {
    super({
      defaultState: sortableTableShellServiceDefaultState as any,
      storeService,
    });
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    // Whenever a row is selected, determine whether it is equal to the current seleted row. If so, unselect the row, otherwise update the selection.
    this.rowSelected$
      .pipe(
        withLatestFrom(this.select('selectedRow', { includeFalsy: true })),
        untilDestroyed(this)
      )
      .subscribe(([row, selectedRow]) => {
        if (row === selectedRow) {
          this.unselectCurrentRow();
        } else {
          this.updateSelectedRow(row);
        }
      });

    // Whenever the dataset changes or a new sort is applied, sort the dataset
    combineLatest([this.select('data'), this.select('sort')])
      .pipe(untilDestroyed(this))
      .subscribe(([data, sort]) => this.handleSort(data, sort));
  }

  data(data: T[]) {
    this.update({ description: 'New dataset available', payload: { data } });
  }

  selectRow(row: T) {
    this.rowSelected$.next(row);
  }

  sort(sort: Sort) {
    this.update({ description: 'New sort available', payload: { sort } });
  }

  private handleSort(data: Dictionary<any>[], { active, direction }: Sort) {
    const sortedData =
      !active || direction === ''
        ? data
        : data
            .slice()
            .sort((a, b) =>
              this.compare(a[active], b[active], direction === 'asc')
            );

    this.update({
      description: 'New sorted dataset available',
      payload: { sortedData },
    });
  }

  private compare(a: number | string, b: number | string, isAsc: boolean) {
    return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
  }

  private updateSelectedRow(selectedRow: T) {
    this.update({
      description: 'New row selected',
      payload: {
        selectedRow,
      },
    });
  }

  private unselectCurrentRow() {
    this.delete({
      description: 'Current row unselected',
      path: ['selectedRow'],
    });
  }
}
