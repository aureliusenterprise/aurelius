import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ControlShellModule } from '../control-shell';
import { FuzzySearchInputComponent } from './fuzzy-search-input.component';

@NgModule({
  imports: [CommonModule, ControlShellModule, FormsModule, ReactiveFormsModule],
  declarations: [FuzzySearchInputComponent],
  exports: [FuzzySearchInputComponent],
})
export class FuzzySearchInputModule {}
