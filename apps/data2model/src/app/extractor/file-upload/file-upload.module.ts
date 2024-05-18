import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FileDropzoneModule } from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';
import { FileUploadRoutingModule } from './file-upload-routing.module';
import { FileUploadComponent } from './file-upload.component';
import { FileUploadService } from './file-upload.service';

@NgModule({
  imports: [
    CommonModule,
    TranslateModule,
    FileUploadRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    FileDropzoneModule
  ],
  declarations: [FileUploadComponent],
  providers: [FileUploadService]
})
export class FileUploadModule {}
