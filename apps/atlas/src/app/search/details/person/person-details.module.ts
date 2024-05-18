import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { GovernanceRolesCardsComponent } from './governance-roles-cards/governance-roles-cards.component';
import { PersonDetailsComponent } from './person-details.component';

@NgModule({
  imports: [
    CommonModule,
    DetailsCardsListModule,
    DetailsNavigationModule,
    GovernanceQualityCardsModule,
    PropertiesModule
  ],
  declarations: [PersonDetailsComponent, GovernanceRolesCardsComponent]
})
export class PersonDetailsModule {}
