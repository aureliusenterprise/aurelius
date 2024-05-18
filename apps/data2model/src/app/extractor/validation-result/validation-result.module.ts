import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ValidationResultComponent } from './validation-result.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [ValidationResultComponent],
  exports: [ValidationResultComponent]
})
export class ValidationResultModule {}
