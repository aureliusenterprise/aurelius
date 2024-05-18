import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DescriptionModule } from '../../components/description/description.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { CollectionsCardsComponent } from './collections-cards/collections-cards.component';
import { ProcessesCardsComponent } from './processes-cards/processes-cards.component';
import { SystemDetailsComponent } from './system-details.component';
import { SystemsCardsComponent } from './systems-cards/systems-cards.component';

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
    CollectionsCardsComponent,
    ProcessesCardsComponent,
    SystemsCardsComponent,
    SystemDetailsComponent
  ],
  exports: [SystemDetailsComponent]
})
export class SystemDetailsModule {}
