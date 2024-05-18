import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ModelCompareComponent } from './model-compare.component';
import { ModelCompareGuard } from './model-compare.guard';
import { ModelCompareResolver } from './model-compare.resolver';

const routes: Routes = [
  {
    path: '',
    component: ModelCompareComponent,
    data: {
      title: extract('Model Compare')
    },
    canActivate: [ModelCompareGuard],
    resolve: { modelCompareParams: ModelCompareResolver }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ModelCompareRoutingModule {}
