import { CommonModule } from '@angular/common';
import { NgModule } from "@angular/core";
import { DataQualityPieModule } from '../data-quality-pie/data-quality-pie.module';
import { DataQualityListComponent } from './data-quality-list.component';

@NgModule({
  imports: [CommonModule, DataQualityPieModule],
  declarations: [DataQualityListComponent],
  exports: [DataQualityListComponent]
})
export class DataQualityListModule {}
