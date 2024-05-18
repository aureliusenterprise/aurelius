import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DetailsCardsListModule } from '../details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsComponent } from './governance-quality-cards.component';

@NgModule({
  imports: [CommonModule, DetailsCardsListModule],
  declarations: [GovernanceQualityCardsComponent],
  exports: [GovernanceQualityCardsComponent]
})
export class GovernanceQualityCardsModule {}
