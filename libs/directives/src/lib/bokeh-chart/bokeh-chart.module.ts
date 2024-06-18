import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BokehChartDirective } from './bokeh-chart.directive';

@NgModule({
  imports: [CommonModule],
  declarations: [BokehChartDirective],
  exports: [BokehChartDirective],
})
export class BokehChartModule {}
