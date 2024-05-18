import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DescriptionModule } from '../../components/description/description.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { LineageModelModule } from '../components/lineage-model/lineage-model.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { InputsCardsComponent } from './inputs-cards/inputs-cards.component';
import { OutputsCardsComponent } from './outputs-cards/outputs-cards.component';
import { ProcessDetailsComponent } from './process-details.component';
import { SystemsCardsComponent } from './systems-cards/systems-cards.component';

@NgModule({
  imports: [
    CommonModule,
    DescriptionModule,
    DetailsCardsListModule,
    DetailsNavigationModule,
    GovernanceQualityCardsModule,
    LineageModelModule,
    PropertiesModule
  ],
  declarations: [
    InputsCardsComponent,
    OutputsCardsComponent,
    ProcessDetailsComponent,
    SystemsCardsComponent
  ],
  exports: [ProcessDetailsComponent]
})
export class ProcessDetailsModule {}
