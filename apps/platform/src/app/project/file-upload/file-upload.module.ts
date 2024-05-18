import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { BranchSelectModule, CommitButtonModule, DescriptionInputModule, FileDropzoneModule } from '@models4insight/components';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { FileUploadRoutingModule } from './file-upload-routing.module';
import { FileUploadComponent } from './file-upload.component';
import { FileUploadGuard } from './file-upload.guard';
import { FileUploadService } from './file-upload.service';

@NgModule({
  imports: [
    CommonModule,
    TranslateModule,
    FileDropzoneModule,
    FileUploadRoutingModule,
    ReactiveFormsModule,
    ProjectPermissionModule,
    BranchPermissionModule,
    BranchSelectModule,
    DescriptionInputModule,
    CommitButtonModule
  ],
  declarations: [FileUploadComponent],
  providers: [FileUploadGuard, FileUploadService]
})
export class FileUploadModule {}
