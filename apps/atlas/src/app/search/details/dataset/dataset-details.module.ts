import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { LineageModelModule } from '../components/lineage-model/lineage-model.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { ConsumersCardsComponent } from './consumers-cards/consumers-cards.component';
import { DatasetDetailsComponent } from './dataset-details.component';
import { DatasetsCardsComponent } from './datasets-cards/datasets-cards.component';
import { EntityCardsComponent } from './entity-cards/entity-cards.component';
import { FieldsCardsComponent } from './fields-cards/fields-cards.component';
import { ProducersCardsComponent } from './producers-cards/producers-cards.component';
import { DescriptionModule } from '../../components/description/description.module';

@NgModule({
  imports: [
    CommonModule,
    DataQualityListModule,
    DescriptionModule,
    DetailsCardsListModule,
    DetailsNavigationModule,
    GovernanceQualityCardsModule,
    LineageModelModule,
    PropertiesModule
  ],
  declarations: [
    ConsumersCardsComponent,
    DatasetDetailsComponent,
    DatasetsCardsComponent,
    EntityCardsComponent,
    FieldsCardsComponent,
    ProducersCardsComponent
  ]
})
export class DatasetDetailsModule {}
