import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BranchNameInputModule } from './branch-name-input';
import { BranchSelectModule } from './branch-select';
import { CreateBranchModalModule } from './create-branch-modal';
import { DescriptionInputModule } from './description-input';
import { FileDropzoneModule } from './file-dropzone';
import { ModalModule } from './modal';
import { SortableTableModule } from './sortable-table/sortable-table.module';
import { I18nService } from '@models4insight/i18n';
import enUS from '../translations/en-US.json';
import nlNL from '../translations/nl-NL.json';

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
export class ComponentsModule {
    constructor(private i18nService: I18nService) {
        this.i18nService.setTranslation('en-US', enUS);
        this.i18nService.setTranslation('nl-NL', nlNL);
    }
}
