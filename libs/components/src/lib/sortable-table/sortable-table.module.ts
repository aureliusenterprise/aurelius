import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MatSortModule } from '@angular/material/sort';
import { SortableTableComponent } from './sortable-table.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { SortableTableShellModule } from '../sortable-table-shell';

@NgModule({
  imports: [
    CommonModule,
    MatSortModule,
    NgxPaginationModule,
    SortableTableShellModule,
  ],
  declarations: [SortableTableComponent],
  exports: [SortableTableComponent],
})
export class SortableTableModule {}
