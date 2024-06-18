import {
  EventEmitter,
  Input,
  OnDestroy,
  Output,
  ViewChild,
  Directive,
} from '@angular/core';
import { Dictionary } from 'lodash';
import { SortableTableShellComponent } from './sortable-table-shell.component';
import { SortableTableShellConfig } from './types';

@Directive()
export abstract class AbstractSortableTable<
  T extends Dictionary<any> = Dictionary<any>
> implements OnDestroy
{
  @ViewChild(SortableTableShellComponent, { static: true })
  table: SortableTableShellComponent<T>;

  ngOnDestroy() {}

  @Input() set config(config: SortableTableShellConfig<T>) {
    this.table.config = config;
  }

  get config() {
    return this.table.config;
  }

  @Input()
  set data(data: T[]) {
    this.table.data = data;
  }

  get data() {
    return this.table.data;
  }

  @Input() set currentPage(currentPage: number) {
    this.table.currentPage = currentPage;
  }

  get currentPage(): number {
    return this.table.currentPage;
  }

  @Input() set enableTableContainer(enabled: boolean) {
    this.table.enableTableContainer = enabled;
  }

  get enableTableContainer() {
    return this.table.enableTableContainer;
  }

  @Input() set itemsPerPage(itemsPerPage: number) {
    this.table.itemsPerPage = itemsPerPage;
  }

  get itemsPerPage() {
    return this.table.itemsPerPage;
  }

  @Input() set rowComparator(
    rowComparator: (value: T, otherValue: T) => boolean
  ) {
    this.table.rowComparator = rowComparator;
  }

  get rowComparator() {
    return this.table.rowComparator;
  }

  @Input() set rowsSelectable(rowsSelectable: boolean) {
    this.table.rowsSelectable = rowsSelectable;
  }

  get rowsSelectable() {
    return this.table.rowsSelectable;
  }

  @Input() set selectedRow(row: T) {
    this.table.selectedRow = row;
  }

  @Input() set showHeaderRow(showHeaderRow: boolean) {
    this.table.showHeaderRow = showHeaderRow;
  }

  get showHeaderRow() {
    return this.table.showHeaderRow;
  }

  @Input() set totalItems(totalItems: number) {
    this.table.totalItems = totalItems;
  }

  get totalItems() {
    return this.table.totalItems;
  }

  @Output() get pageChanged(): EventEmitter<number> {
    return this.table.pageChanged;
  }

  @Output() get rowClicked(): EventEmitter<T> {
    return this.table.rowClicked;
  }

  @Output() get rowDeselected(): EventEmitter<void> {
    return this.table.rowDeselected;
  }

  @Output() get rowIntersectionChanged(): EventEmitter<[T, boolean]> {
    return this.table.rowIntersectionChanged;
  }

  @Output() get rowSelected(): EventEmitter<T> {
    return this.table.rowSelected;
  }
}
