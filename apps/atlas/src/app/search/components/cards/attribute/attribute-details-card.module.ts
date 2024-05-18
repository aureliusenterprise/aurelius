import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BreadCrumbsModule } from '../../bread-crumbs/bread-crumbs.module';
import { ClassificationsListModule } from '../../classifications-list/classifications-list.module';
import { DataQualityListModule } from '../../data-quality-list/data-quality-list.module';
import { DescriptionModule } from '../../description/description.module';
import { PeopleModule } from '../../people/people.module';
import { AttributeDetailsCardComponent } from './attribute-details-card.component';

@NgModule({
  imports: [
    CommonModule,
    PeopleModule,
    DescriptionModule,
    ClassificationsListModule,
    BreadCrumbsModule,
    DataQualityListModule
  ],
  declarations: [AttributeDetailsCardComponent],
  exports: [AttributeDetailsCardComponent]
})
export class AttributeDetailsCardModule {}
