import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BreadCrumbsModule } from '../../bread-crumbs/bread-crumbs.module';
import { ClassificationsListModule } from '../../classifications-list/classifications-list.module';
import { DataQualityListModule } from '../../data-quality-list/data-quality-list.module';
import { FieldDetailsCardComponent } from './field-details-card.component';

@NgModule({
  imports: [
    CommonModule,
    ClassificationsListModule,
    BreadCrumbsModule,
    DataQualityListModule
  ],
  declarations: [FieldDetailsCardComponent],
  exports: [FieldDetailsCardComponent]
})
export class FieldDetailsCardModule {}
