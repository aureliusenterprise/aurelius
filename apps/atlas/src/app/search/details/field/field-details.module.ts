import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DescriptionModule } from '../../components/description/description.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { AttributesCardsComponent } from './attributes-cards/attributes-cards.component';
import { DataQualityCardsComponent } from './data-quality-cards/data-quality-cards.component';
import { FieldDetailsComponent } from './field-details.component';
import { FieldsCardsComponent } from './fields-cards/fields-cards.component';

@NgModule({
  imports: [
    CommonModule,
    DataQualityListModule,
    DescriptionModule,
    DetailsCardsListModule,
    DetailsNavigationModule,
    GovernanceQualityCardsModule,
    PropertiesModule
  ],
  declarations: [
    AttributesCardsComponent,
    DataQualityCardsComponent,
    FieldDetailsComponent,
    FieldsCardsComponent
  ]
})
export class FieldDetailsModule {}
