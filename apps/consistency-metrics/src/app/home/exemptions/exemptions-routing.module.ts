import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ExemptionsComponent } from './exemptions.component';

const routes: Routes = [
  {
    path: '',
    component: ExemptionsComponent,
    data: { title: 'Exemptions' }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ExemptionsRoutingModule {}
