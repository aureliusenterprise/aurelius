import { Component } from '@angular/core';
import { Dictionary } from 'lodash';
import { AbstractSortableTable } from '../sortable-table-shell';

@Component({
  selector: 'models4insight-sortable-table',
  templateUrl: 'sortable-table.component.html',
  styleUrls: ['sortable-table.component.scss'],
})
export class SortableTableComponent<
  T extends Dictionary<any> = Dictionary<any>
> extends AbstractSortableTable<T> {
  sortByKeyOrder() {
    return 0;
  }

  trackByIndex(data: T, index: number) {
    return index;
  }
}
