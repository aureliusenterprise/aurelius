import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ControlShellModule } from '../control-shell';
import { SimpleSearchInputComponent } from './simple-search-input.component';

@NgModule({
  imports: [CommonModule, ControlShellModule, FontAwesomeModule],
  declarations: [SimpleSearchInputComponent],
  exports: [SimpleSearchInputComponent],
})
export class SimpleSearchInputModule {}
