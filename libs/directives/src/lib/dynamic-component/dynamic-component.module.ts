import { NgModule } from '@angular/core';
import { DynamicComponentDirective } from './dynamic-component.directive';

@NgModule({
  declarations: [DynamicComponentDirective],
  exports: [DynamicComponentDirective],
})
export class DynamicComponentModule {}
