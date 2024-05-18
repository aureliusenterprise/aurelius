import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SortableTableModule } from '@models4insight/components';
import { DatasetRoutingModule } from './dataset-routing.module';
import { DatasetComponent } from './dataset.component';
import { DatasetService } from './dataset.service';

@NgModule({
  imports: [CommonModule, DatasetRoutingModule, SortableTableModule],
  declarations: [DatasetComponent],
  providers: [DatasetService]
})
export class DatasetModule {}
