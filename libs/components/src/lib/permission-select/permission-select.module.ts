import { NgModule } from '@angular/core';
import { PermissionSelectComponent } from './permission-select.component';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SelectModule } from '../select';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, SelectModule],
  declarations: [PermissionSelectComponent],
  exports: [PermissionSelectComponent],
})
export class PermissionSelectModule {}
