import { Component, Input, ViewChild } from '@angular/core';
import { SubType, untilDestroyed } from '@models4insight/utils';
import { Dictionary, isEqual, toLower } from 'lodash';
import { BehaviorSubject, combineLatest } from 'rxjs';
import { startWith } from 'rxjs/operators';
import { DatePickerComponent } from '../../date-picker';
import { FuzzySearchInputComponent } from '../../fuzzy-search-input';
import { AbstractModal, ModalContext } from '../../modal';
import { SortableTableComponent } from '../../sortable-table';
import { SortableTableShellConfig } from '../../sortable-table-shell';
import { Select } from '../select';

@Component({
  selector: 'models4insight-search-modal',
  templateUrl: 'search-modal.component.html',
  styleUrls: ['search-modal.component.scss'],
})
export class SearchModalComponent<
  T extends Dictionary<any>
> extends AbstractModal {
  @Input() control: Select;
  @Input() isTimestamp = false;
  @Input() modalContext: ModalContext;
  @Input() rowComparator: (value: T, otherValue: T) => boolean = isEqual;
  @Input() tableConfig: SortableTableShellConfig;

  filteredRows: T[] = [];
  rows: T[] = [];
  rowsByKey: Dictionary<T> = {};
  searchQuery: string | number = '';
  searchResult: string[] = [];
  searchTerms: string[] = [];

  private readonly isLoading$ = new BehaviorSubject<boolean>(false);

  private searchKey: keyof SubType<T, string | number>;

  get isLoading() {
    return this.isLoading$.asObservable();
  }

  @Input() set data(data: T[]) {
    this.rows = data;
    this.updateRowIndex();
  }

  @Input() set displayField(displayField: keyof SubType<T, string | number>) {
    this.searchKey = displayField;
    this.updateRowIndex();
  }

  @ViewChild(DatePickerComponent, { static: false }) set datepicker(
    datepicker: DatePickerComponent
  ) {
    if (datepicker) {
      // Whenever the user selects a date, search for items within a timespan of a day
      datepicker.dateChanged
        .pipe(untilDestroyed(datepicker))
        .subscribe((lowerBound) => {
          this.searchQuery = lowerBound;
          if (lowerBound) {
            const upperBound = lowerBound + 24 * 60 * 60 * 1000; //ms = 1 day;
            this.searchResult = this.searchTerms.filter((term) => {
              const timestamp = Number.parseInt(term, 10);
              return lowerBound <= timestamp && upperBound > timestamp;
            });
          } else {
            this.searchResult = this.searchTerms;
          }

          this.updateFilteredRows();
        });
    }
  }

  @ViewChild(FuzzySearchInputComponent, { static: false }) set searchInput(
    searchInput: FuzzySearchInputComponent<T>
  ) {
    if (searchInput) {
      searchInput.tokenizerConfig = {
        [this.searchKey as any]: {},
      };

      searchInput.isUpdatingSearchIndex$
        .pipe(untilDestroyed(searchInput))
        .subscribe(this.isLoading$);

      searchInput.queryChanged
        .pipe(untilDestroyed(searchInput))
        .subscribe((query) => (this.searchQuery = query));

      combineLatest([
        searchInput.queryChanged.pipe(startWith(this.searchQuery)),
        searchInput.suggestionsChanged.pipe(startWith([] as T[])),
      ])
        .pipe(untilDestroyed(searchInput))
        .subscribe(([searchQuery, searchResult]) => {
          this.searchQuery = searchQuery;
          this.filteredRows = searchQuery ? searchResult : this.rows;
        });
    }
  }

  @ViewChild(SortableTableComponent, { static: false })
  set searchTable(searchTable: SortableTableComponent<T>) {
    if (searchTable) {
      searchTable.rowClicked
        .pipe(untilDestroyed(searchTable))
        .subscribe((value) => {
          this.control.setValue(value);
          this.modal.confirm();
        });
    }
  }

  private updateFilteredRows() {
    if (!this.searchResult || this.searchResult.length === 0) {
      if (this.searchQuery) {
        this.filteredRows = [];
      } else {
        this.filteredRows = this.rows;
      }
    } else {
      this.filteredRows = this.searchResult.map(
        (suggestion) => this.rowsByKey[suggestion]
      );
    }
  }

  private updateRowIndex() {
    if (this.rows && this.searchKey) {
      this.rowsByKey = this.rows.reduce(
        (rowsByKey, row) => ({
          ...rowsByKey,
          [toLower(row[this.searchKey])]: row,
        }),
        {}
      );
      this.searchTerms = Object.keys(this.rowsByKey);
      this.updateFilteredRows();
    }
  }
}
