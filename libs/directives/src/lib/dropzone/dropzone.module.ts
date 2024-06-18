import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DropzoneDirective } from './dropzone.directive';

@NgModule({
  imports: [CommonModule],
  declarations: [DropzoneDirective],
  exports: [DropzoneDirective],
})
export class DropzoneModule {}
