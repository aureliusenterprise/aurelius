import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DescriptionModule } from '../../components/description/description.module';
import { PeopleModule } from '../../components/people/people.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { AttributesCardsComponent } from './attributes-cards/attributes-cards.component';
import { DatasetsCardsComponent } from './datasets-cards/datasets-cards.component';
import { EntitiesCardsComponent } from './entities-cards/entities-cards.component';
import { EntityDetailsComponent } from './entity-details.component';

@NgModule({
  imports: [
    CommonModule,
    DataQualityListModule,
    DescriptionModule,
    DetailsCardsListModule,
    DetailsNavigationModule,
    GovernanceQualityCardsModule,
    PeopleModule,
    PropertiesModule
  ],
  declarations: [
    AttributesCardsComponent,
    DatasetsCardsComponent,
    EntitiesCardsComponent,
    EntityDetailsComponent
  ]
})
export class EntityDetailsModule {}
