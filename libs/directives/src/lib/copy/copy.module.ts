import { NgModule } from '@angular/core';
import { CopyDirective } from './copy.directive';

@NgModule({
  declarations: [CopyDirective],
  exports: [CopyDirective],
})
export class CopyModule {}
