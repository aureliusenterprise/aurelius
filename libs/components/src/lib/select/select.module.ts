import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { FuzzySearchInputModule } from '../fuzzy-search-input';
import { ModalModule } from '../modal';
import { SortableTableModule } from '../sortable-table';
import { SearchModalComponent } from './search-modal/search-modal.component';
import { SelectComponent } from './select.component';
import { DatePickerModule } from '../date-picker';
import { ControlShellModule } from '../control-shell';

@NgModule({
  imports: [
    CommonModule,
    ControlShellModule,
    DatePickerModule,
    FontAwesomeModule,
    FormsModule,
    FuzzySearchInputModule,
    ReactiveFormsModule,
    ModalModule,
    SortableTableModule,
  ],
  declarations: [SearchModalComponent, SelectComponent],
  exports: [SelectComponent],
})
export class SelectModule {}
