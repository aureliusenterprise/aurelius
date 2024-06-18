import {
  Component,
  ContentChild,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  TemplateRef,
} from '@angular/core';
import { Sort } from '@angular/material/sort';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary, isEqual } from 'lodash';
import { Observable, partition } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { SortableTableShellService } from './sortable-table-shell.service';
import { SortableTableShellConfig } from './types';

@Component({
  selector: 'models4insight-sortable-table-shell',
  templateUrl: 'sortable-table-shell.component.html',
  styleUrls: ['sortable-table-shell.component.scss'],
  viewProviders: [SortableTableShellService],
})
export class SortableTableShellComponent<
  T extends Dictionary<any> = Dictionary<any>
> implements OnInit, OnDestroy
{
  @ContentChild(TemplateRef, { static: true })
  readonly row: TemplateRef<any>;

  @Output() readonly pageChanged: EventEmitter<number> =
    new EventEmitter<number>();
  @Output() readonly rowClicked: EventEmitter<T> = new EventEmitter<T>();
  @Output() readonly rowSelected: EventEmitter<T> = new EventEmitter<T>();
  @Output() readonly rowDeselected: EventEmitter<void> =
    new EventEmitter<void>();
  @Output() readonly rowIntersectionChanged: EventEmitter<[T, boolean]> =
    new EventEmitter<[T, boolean]>();

  @Input() config: SortableTableShellConfig<T> = {};
  @Input() enableTableContainer = true;
  @Input() itemsPerPage = 10;
  @Input() rowComparator: (value: T, otherValue: T) => boolean = isEqual;
  @Input() rowsSelectable = true;
  @Input() showHeaderRow = true;
  @Input() totalItems: number;

  readonly paginationId = uuid();

  currentPage$: Observable<number>;
  selectedRow$: Observable<T>;
  sort$: Observable<Sort>;
  sortedData$: Observable<T[]>;

  constructor(private sortableTableService: SortableTableShellService<T>) {}

  ngOnInit() {
    this.selectedRow$ = this.sortableTableService
      .select('selectedRow', {
        includeFalsy: true,
      })
      .pipe(shareReplay());

    // Emit specific events for when a row gets selected or deselected. A row is deselected if it is undefined
    const [selected, deselected] = partition(this.selectedRow$, (row) => !!row);

    deselected
      .pipe(untilDestroyed(this))
      .subscribe(() => this.rowDeselected.emit());
    selected.pipe(untilDestroyed(this)).subscribe(this.rowSelected);

    this.currentPage$ = this.sortableTableService.select('currentPage');
    this.sort$ = this.sortableTableService.select('sort').pipe(shareReplay());
    this.sortedData$ = this.sortableTableService.select('sortedData');
  }

  ngOnDestroy() {}

  isRowSelected(row: T, selection: T) {
    return this.rowComparator(row, selection);
  }

  onRowClicked(row: T) {
    this.rowClicked.emit(row);
    if (this.rowsSelectable) {
      this.sortableTableService.selectRow(row);
    }
  }

  onRowIntersectionChanged(row: T, isIntersecting: boolean) {
    this.rowIntersectionChanged.emit([row, isIntersecting]);
  }

  sortByKeyOrder() {
    return 0;
  }

  trackByIndex(index: number) {
    return index;
  }

  @Input() set data(data: T[]) {
    this.sortableTableService.data(data);
  }

  @Input() set currentPage(currentPage: number) {
    this.sortableTableService.update({
      description: 'New page selected',
      payload: { currentPage },
    });
    this.pageChanged.emit(currentPage);
  }

  @Input() set selectedRow(row: T) {
    this.sortableTableService.update({
      description: 'New row selected',
      payload: { selectedRow: row },
    });
  }

  @Input() set sort(sort: Sort) {
    this.sortableTableService.sort(sort);
  }
}
