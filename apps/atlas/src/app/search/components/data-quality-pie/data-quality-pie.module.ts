import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataQualityPieComponent } from './data-quality-pie.component';

@NgModule({
  imports: [CommonModule],
  declarations: [DataQualityPieComponent],
  exports: [DataQualityPieComponent]
})
export class DataQualityPieModule {}
