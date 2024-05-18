import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { DomainsWizardComponent } from './domains-wizard.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [DomainsWizardComponent],
  exports: [DomainsWizardComponent],
})
export class DomainsWizardModule {}
