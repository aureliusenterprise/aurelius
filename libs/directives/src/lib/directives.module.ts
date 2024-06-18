import { NgModule } from '@angular/core';
import { BokehChartModule } from './bokeh-chart/bokeh-chart.module';
import { DropzoneModule } from './dropzone/dropzone.module';
import { HoldableModule } from './holdable/holdable.module';

@NgModule({
  imports: [BokehChartModule, DropzoneModule, HoldableModule],
  exports: [BokehChartModule, DropzoneModule, HoldableModule],
})
export class DirectivesModule {}
