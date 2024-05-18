import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { CollectionDetailsComponent } from './collection-details.component';
import { DatasetsCardsComponent } from './datasets-cards/datasets-cards.component';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { DescriptionModule } from '../../components/description/description.module';

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
  declarations: [DatasetsCardsComponent, CollectionDetailsComponent]
})
export class CollectionDetailsModule {}
