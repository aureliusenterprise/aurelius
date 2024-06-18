import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MatSortModule } from '@angular/material/sort';
import { IntersectionObserverModule } from '@models4insight/directives';
import { NgxPaginationModule } from 'ngx-pagination';
import { SortableTableShellComponent } from './sortable-table-shell.component';

@NgModule({
  imports: [
    CommonModule,
    IntersectionObserverModule,
    MatSortModule,
    NgxPaginationModule,
  ],
  declarations: [SortableTableShellComponent],
  exports: [SortableTableShellComponent],
})
export class SortableTableShellModule {}
