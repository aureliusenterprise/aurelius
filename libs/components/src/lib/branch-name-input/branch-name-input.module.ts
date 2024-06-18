import { NgModule } from '@angular/core';
import { BranchNameInputComponent } from './branch-name-input.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ControlShellModule } from '../control-shell';

@NgModule({
  imports: [CommonModule, ControlShellModule, FormsModule, ReactiveFormsModule],
  declarations: [BranchNameInputComponent],
  exports: [BranchNameInputComponent],
})
export class BranchNameInputModule {}
