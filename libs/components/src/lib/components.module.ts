import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BranchNameInputModule } from './branch-name-input';
import { BranchSelectModule } from './branch-select';
import { CreateBranchModalModule } from './create-branch-modal';
import { DescriptionInputModule } from './description-input';
import { FileDropzoneModule } from './file-dropzone';
import { ModalModule } from './modal';
import { SortableTableModule } from './sortable-table/sortable-table.module';

@NgModule({
  imports: [
    CommonModule,
    SortableTableModule,
    BranchNameInputModule,
    BranchSelectModule,
    CreateBranchModalModule,
    ModalModule,
    FileDropzoneModule,
    DescriptionInputModule,
  ],
  exports: [
    SortableTableModule,
    BranchNameInputModule,
    BranchSelectModule,
    CreateBranchModalModule,
    ModalModule,
    FileDropzoneModule,
    DescriptionInputModule,
  ],
})
export class ComponentsModule {}
