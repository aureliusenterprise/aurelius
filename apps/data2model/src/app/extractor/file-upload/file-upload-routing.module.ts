import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { FileUploadComponent } from './file-upload.component';


const routes: Routes = [
    {
        path: '',
        component: FileUploadComponent,
        data: {
            title: extract('Upload some data')
        },
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: []
})
export class FileUploadRoutingModule { }
