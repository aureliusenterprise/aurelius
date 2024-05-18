import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BreadCrumbsModule } from '../../bread-crumbs/bread-crumbs.module';
import { ClassificationsListModule } from '../../classifications-list/classifications-list.module';
import { DataQualityListModule } from '../../data-quality-list/data-quality-list.module';
import { CollectionDetailsCardComponent } from './collection-details-card.component';

@NgModule({
  imports: [
    CommonModule,
    ClassificationsListModule,
    BreadCrumbsModule,
    DataQualityListModule
  ],
  declarations: [CollectionDetailsCardComponent],
  exports: [CollectionDetailsCardComponent]
})
export class CollectionDetailsCardModule {}
