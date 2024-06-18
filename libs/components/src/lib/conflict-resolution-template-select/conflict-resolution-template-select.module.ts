import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConflictResolutionTemplateSelectComponent } from './conflict-resolution-template-select.component';
import { SelectModule } from '../select';

@NgModule({
  imports: [CommonModule, SelectModule],
  declarations: [ConflictResolutionTemplateSelectComponent],
  exports: [ConflictResolutionTemplateSelectComponent],
})
export class ConflictResolutionTemplateSelectModule {}
