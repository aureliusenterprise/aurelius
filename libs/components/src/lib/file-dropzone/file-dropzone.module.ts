import { NgModule } from '@angular/core';
import { DropzoneModule } from '@models4insight/directives';
import { CommonModule } from '@angular/common';
import { FileDropzoneComponent } from './file-dropzone.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ControlShellModule } from '../control-shell';

@NgModule({
  imports: [
    CommonModule,
    ControlShellModule,
    DropzoneModule,
    FontAwesomeModule,
  ],
  declarations: [FileDropzoneComponent],
  exports: [FileDropzoneComponent],
})
export class FileDropzoneModule {}
