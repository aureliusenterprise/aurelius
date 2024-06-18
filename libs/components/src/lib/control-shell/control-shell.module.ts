import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ControlShellComponent } from './control-shell.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [ControlShellComponent],
  exports: [ControlShellComponent, FormsModule, ReactiveFormsModule],
})
export class ControlShellModule {}
