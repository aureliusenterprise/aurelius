import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SelectModule } from '@models4insight/components';
import { TypeSelectComponent } from './type-select.component';

@NgModule({
  imports: [CommonModule, SelectModule],
  declarations: [TypeSelectComponent],
  exports: [TypeSelectComponent]
})
export class TypeSelectModule {}
