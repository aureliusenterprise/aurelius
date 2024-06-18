import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DescriptionInputComponent } from './description-input.component';
import { ControlShellModule } from '../control-shell';

@NgModule({
  imports: [CommonModule, ControlShellModule, FormsModule, ReactiveFormsModule],
  declarations: [DescriptionInputComponent],
  exports: [DescriptionInputComponent],
})
export class DescriptionInputModule {}
