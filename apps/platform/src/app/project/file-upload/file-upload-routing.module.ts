import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { FileUploadComponent } from './file-upload.component';
import { FileUploadGuard } from './file-upload.guard';

const routes: Routes = [
  {
    path: '',
    component: FileUploadComponent,
    data: {
      title: extract('Upload a Model')
    },
    canActivate: [FileUploadGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class FileUploadRoutingModule {}
