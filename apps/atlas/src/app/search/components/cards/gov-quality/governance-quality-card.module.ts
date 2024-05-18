import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { GovernanceQualityCardComponent } from './governance-quality-card.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, TranslateModule.forChild()],
  declarations: [GovernanceQualityCardComponent],
  exports: [GovernanceQualityCardComponent]
})
export class GovernanceQualityCardModule {}
