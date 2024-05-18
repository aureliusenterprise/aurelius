import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SummaryWizardComponent } from './summary-wizard.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [SummaryWizardComponent],
  exports: [SummaryWizardComponent],
})
export class SummaryWizardModule {}
