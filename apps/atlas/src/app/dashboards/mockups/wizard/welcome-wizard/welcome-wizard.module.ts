import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { WelcomeWizardComponent } from './welcome-wizard.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [WelcomeWizardComponent],
  exports: [WelcomeWizardComponent],
})
export class WelcomeWizardModule {}
