import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DetailsCardsListModule } from '../details-cards-list/details-cards-list.module';
import { GovernanceQualityCardsComponent } from './governance-quality-cards.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, DetailsCardsListModule, TranslateModule],
    declarations: [GovernanceQualityCardsComponent],
    exports: [GovernanceQualityCardsComponent],
})
export class GovernanceQualityCardsModule {}
