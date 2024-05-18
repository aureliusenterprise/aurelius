import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SystemsWizardComponent } from './systems-wizard.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [SystemsWizardComponent],
  exports: [SystemsWizardComponent],
})
export class SystemsWizardModule {}
