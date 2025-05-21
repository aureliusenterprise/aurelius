import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DescriptionModule } from '../../components/description/description.module';
import { DataQualityPieModule } from '../../components/data-quality-pie/data-quality-pie.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { CompliantCardsComponent } from './compliant-cards/compliant-cards.component';
import { GovQualityDetailsComponent } from './gov-quality-details.component';
import { NonCompliantCardsComponent } from './non-compliant-cards/non-compliant-cards.component';

@NgModule({
  imports: [
    CommonModule,
    DetailsNavigationModule,
    PropertiesModule,
    DataQualityPieModule,
    DescriptionModule,
    DetailsCardsListModule,
  ],
  declarations: [
    GovQualityDetailsComponent,
    CompliantCardsComponent,
    NonCompliantCardsComponent,
  ],
})
export class GovQualityDetailsModule {}
