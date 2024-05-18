import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { BreadCrumbsModule } from '../../bread-crumbs/bread-crumbs.module';
import { DataQualityPieModule } from '../../data-quality-pie/data-quality-pie.module';
import { DataQualityCardComponent } from './data-quality-card.component';

@NgModule({
  imports: [
    CommonModule,
    TranslateModule.forChild(),
    BreadCrumbsModule,
    DataQualityPieModule
  ],
  declarations: [DataQualityCardComponent],
  exports: [DataQualityCardComponent]
})
export class DataQualityCardModule {}
