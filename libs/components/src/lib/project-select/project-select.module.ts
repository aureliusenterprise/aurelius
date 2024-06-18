import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SelectModule } from '../select';
import { ProjectSelectComponent } from './project-select.component';

@NgModule({
  imports: [CommonModule, FormsModule, ReactiveFormsModule, SelectModule],
  declarations: [ProjectSelectComponent],
  exports: [ProjectSelectComponent],
})
export class ProjectSelectModule {}
