import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { DatasetComponent } from './dataset.component';

const routes: Routes = [
  {
    path: '',
    component: DatasetComponent,
    data: {
      title: extract('Review the dataset')
    }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class DatasetRoutingModule {}
