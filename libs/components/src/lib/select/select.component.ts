import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { faSearch, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { Dictionary, isEqual } from 'lodash';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';
import { ModalContext } from '../modal';
import { SortableTableShellConfig } from '../sortable-table-shell';
import { SearchModalComponent } from './search-modal/search-modal.component';

export interface SelectContext extends ControlShellContext {
  /** The icon that should be shown as part of the select menu */
  readonly icon?: IconDefinition;
  /** Whether or not the display field represents a timestamp */
  readonly isTimestamp?: boolean;
  /** The label to show on top of the select menu */
  readonly label?: string;
  /** The message to show when no options are available */
  readonly noDataMessage?: string;
  /** The message to show when no option is selected */
  readonly nullInputMessage?: string;
  /** The configuration options for the search modal */
  readonly searchModalContext?: ModalContext;
  /** The configuration options for the table in the search modal */
  readonly searchTableConfig?: SortableTableShellConfig;
}

export const defaultSelectContext: SelectContext = {
  ...defaultControlShellContext,
  label: 'Title',
  isTimestamp: false,
  noDataMessage: 'No data available',
  nullInputMessage: 'Please select a value',
  requiredErrorMessage: 'Please select a value',
  searchModalContext: {
    cancel: 'Close',
    closeOnConfirm: true,
    title: 'Search for a value',
  },
};

@Component({
  selector: 'models4insight-select',
  templateUrl: 'select.component.html',
  styleUrls: ['select.component.scss'],
})
export class SelectComponent<T extends Dictionary<any> = Dictionary<any>>
  extends AbstractControlShell
  implements OnInit
{
  @Input() comparator: (a: T, b: T) => boolean = isEqual;
  @Input() data: T[] = [];
  @Input() displayField: keyof T;
  @Input() isDisabled = false;

  @ViewChild(SearchModalComponent, { static: true })
  private readonly searchModal: SearchModalComponent<T>;

  readonly faSearch = faSearch;

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultSelectContext;
    }
  }

  activateSearchModal() {
    this.searchModal.activate();
  }

  trackByIndex(index: number) {
    return index;
  }

  get isLoading() {
    return this.searchModal.isLoading;
  }
}
